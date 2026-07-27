from pathlib import Path
import pandas as pd

from pathlib import Path
import pandas as pd

from pathlib import Path
import pandas as pd

DATA_DIR = Path("/Users/vedikabaradwaj/Documents/pdi_pensions/data/csv")
OUTPUT_DIR = Path.home() / "Downloads"

YEAR_PAIRS = [
    (2008, 2009),
    (2009, 2010),
    (2010, 2011), 
    (2011, 2012),
    (2012, 2013), 
    (2013, 2014), 
    (2014, 2015),
    (2015, 2016),
    (2016, 2017)
]

def load_morg(path: Path, year: int) -> pd.DataFrame:
    if not path.exists():
        print(f"Skipping {year}: file not found -> {path.name}")
        return None

    print(f"Loading {path} ...", flush=True)

    # Read key merge columns as strings immediately
    df = pd.read_csv(
        path,
        low_memory=False,
        dtype={
            "hhid": "string",
            "hhnum": "string",
            "lineno": "string",
            "intmonth": "string",
            "stfips": "string",
            "state": "string",
        }
    )

    df.columns = df.columns.str.lower().str.strip()

    # Prefer stfips over state
    if "stfips" not in df.columns and "state" in df.columns:
        df["stfips"] = df["state"]

    required_basic = ["hhid", "hhnum", "lineno", "intmonth", "minsamp", "sex", "race", "stfips"]
    missing = [c for c in required_basic if c not in df.columns]
    if missing:
        print(f"Skipping {path.name}: missing columns {missing}")
        return None

    for col in ["hhid", "hhnum", "lineno", "intmonth", "stfips"]:
        df[col] = df[col].astype("string").str.strip()

    for col in ["minsamp", "sex", "race"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year_file"] = year

    print(f"  {len(df):,} records loaded.")
    print("  minsamp counts:")
    print(df["minsamp"].value_counts(dropna=False).sort_index())

    return df


def restrict_to_morg(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df[df["minsamp"].isin([4, 8])].copy()
    print(f"  After minsamp filter: {len(df):,} (dropped {before - len(df):,})")
    return df


def build_rename_map(df: pd.DataFrame, suffix: str, merge_keys: list[str]) -> dict:
    rename = {}
    for col in df.columns:
        if col not in merge_keys and col not in ["minsamp", "year_file"]:
            rename[col] = f"{col}{suffix}"
    return rename


def debug_overlap(t_df: pd.DataFrame, t1_df: pd.DataFrame, merge_keys: list[str], label: str):
    print(f"\nDEBUG: {label}")
    print("Merge keys:", merge_keys)

    # Create composite key just to inspect overlap
    key_t = t_df[merge_keys].astype(str).agg("|".join, axis=1)
    key_t1 = t1_df[merge_keys].astype(str).agg("|".join, axis=1)

    overlap = len(set(key_t).intersection(set(key_t1)))

    print(f"  t rows: {len(t_df):,}")
    print(f"  t1 rows: {len(t1_df):,}")
    print(f"  unique composite keys in t: {key_t.nunique():,}")
    print(f"  unique composite keys in t1: {key_t1.nunique():,}")
    print(f"  overlapping composite keys: {overlap:,}")

    for k in merge_keys:
        print(f"  Sample {k} values t:", t_df[k].dropna().astype(str).head(3).tolist())
        print(f"  Sample {k} values t1:", t1_df[k].dropna().astype(str).head(3).tolist())


def create_panel(df_t: pd.DataFrame, df_t1: pd.DataFrame) -> pd.DataFrame:
    merge_keys = ["hhid", "hhnum", "lineno", "intmonth", "stfips"]

    pairs = [
        (df_t[df_t["minsamp"] == 4].copy(), df_t1[df_t1["minsamp"] == 8].copy(), "MIS4_to_MIS8"),
        (df_t[df_t["minsamp"] == 8].copy(), df_t1[df_t1["minsamp"] == 4].copy(), "MIS8_to_MIS4"),
    ]

    out = []
    for t_df, t1_df, label in pairs:
        debug_overlap(t_df, t1_df, merge_keys, label)

        t_df = t_df.rename(columns=build_rename_map(t_df, "_t", merge_keys))
        t1_df = t1_df.rename(columns=build_rename_map(t1_df, "_t1", merge_keys))

        merged = pd.merge(
            t_df,
            t1_df,
            on=merge_keys,
            how="inner",
        )
        merged["pair_type"] = label

        print(f"[{label}] {len(merged):,} matches ({len(t_df):,} vs {len(t1_df):,})")
        out.append(merged)

    if not out:
        return pd.DataFrame()

    return pd.concat(out, ignore_index=True)


def apply_sra_filter(df: pd.DataFrame):
    sex_mismatch = df["sex_t"] != df["sex_t1"]
    race_mismatch = df["race_t"] != df["race_t1"]

    invalid_mask = sex_mismatch | race_mismatch

    valid = df.loc[~invalid_mask].copy()
    invalid = df.loc[invalid_mask].copy()

    return valid, invalid

def weighted_mean(df, x_col, w_col):
    if x_col not in df.columns or w_col not in df.columns:
        return np.nan

    x = pd.to_numeric(df[x_col], errors="coerce")
    w = pd.to_numeric(df[w_col], errors="coerce")

    ok = x.notna() & w.notna() & (w > 0)
    if ok.sum() == 0:
        return np.nan

    return (x[ok] * w[ok]).sum() / w[ok].sum()


def summarize_sample(df, pair, stage):
    """
    Creates one row of descriptive characteristics for a sample.
    This assumes post-merge suffixes like age_t, sex_t, race_t, earnwke_t, etc.
    For raw yearly files, it also works with unsuffixed names.
    """

    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    # Prefer t variables if they exist; otherwise use raw unsuffixed versions
    age_col = "age_t" if "age_t" in df.columns else "age"
    sex_col = "sex_t" if "sex_t" in df.columns else "sex"
    race_col = "race_t" if "race_t" in df.columns else "race"
    earn_col = "earnwke_t" if "earnwke_t" in df.columns else "earnwke"
    hours_col = "uhourse_t" if "uhourse_t" in df.columns else "uhourse"
    class_col = "class94_t" if "class94_t" in df.columns else "class94"
    weight_col = (
        "weight_t" if "weight_t" in df.columns else
        "wtfinl_t" if "wtfinl_t" in df.columns else
        "weight" if "weight" in df.columns else
        "wtfinl" if "wtfinl" in df.columns else
        None
    )

    # If no weight exists, use unweighted means
    if weight_col is None:
        df["_unit_weight"] = 1
        weight_col = "_unit_weight"

    # Convert numeric columns safely
    for col in [age_col, sex_col, race_col, earn_col, hours_col, class_col, weight_col]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    row = {
        "pair": pair,
        "stage": stage,
        "N": len(df),
        "weighted_N": df[weight_col].sum() if weight_col in df.columns else np.nan,
    }

    if age_col in df.columns:
        row["mean_age"] = weighted_mean(df, age_col, weight_col)
        row["share_age_le_30"] = weighted_mean(df.assign(_x=(df[age_col] <= 30).astype(float)), "_x", weight_col)
        row["share_age_55_plus"] = weighted_mean(df.assign(_x=(df[age_col] >= 55).astype(float)), "_x", weight_col)
        row["share_age_60_plus"] = weighted_mean(df.assign(_x=(df[age_col] >= 60).astype(float)), "_x", weight_col)

    if sex_col in df.columns:
        # CPS sex is usually 1 = male, 2 = female
        row["female_share"] = weighted_mean(df.assign(_x=(df[sex_col] == 2).astype(float)), "_x", weight_col)

    if race_col in df.columns:
        # Common CPS race coding: 1 = White, 2 = Black
        row["white_share"] = weighted_mean(df.assign(_x=(df[race_col] == 1).astype(float)), "_x", weight_col)
        row["black_share"] = weighted_mean(df.assign(_x=(df[race_col] == 2).astype(float)), "_x", weight_col)
        row["other_race_share"] = weighted_mean(
            df.assign(_x=((~df[race_col].isin([1, 2])) & df[race_col].notna()).astype(float)),
            "_x",
            weight_col
        )

    if earn_col in df.columns:
        row["mean_weekly_earnings"] = weighted_mean(df, earn_col, weight_col)
        df["_annual_earnings"] = df[earn_col] * 52
        row["mean_annual_earnings"] = weighted_mean(df, "_annual_earnings", weight_col)

    if hours_col in df.columns:
        row["mean_usual_hours"] = weighted_mean(df, hours_col, weight_col)

    if class_col in df.columns:
        row["public_share"] = weighted_mean(df.assign(_x=df[class_col].isin([1, 2, 3]).astype(float)), "_x", weight_col)
        row["state_local_public_share"] = weighted_mean(df.assign(_x=df[class_col].isin([2, 3]).astype(float)), "_x", weight_col)

    return row


def main():
    attrition_rows = []
    characteristics_rows = []

    for y0, y1 in YEAR_PAIRS:
        print("\n" + "=" * 80)
        print(f"PROCESSING {y0}-{y1}")
        print("=" * 80)

        pair_label = f"{y0}-{y1}"

        f0 = DATA_DIR / f"morg{str(y0)[-2:]}.csv"
        f1 = DATA_DIR / f"morg{str(y1)[-2:]}.csv"

        df0_raw = load_morg(f0, y0)
        df1_raw = load_morg(f1, y1)

        if df0_raw is None or df1_raw is None:
            print(f"Skipping pair {y0}-{y1}")
            continue

        raw_t_N = len(df0_raw)
        raw_t1_N = len(df1_raw)

        characteristics_rows.append(
            summarize_sample(df0_raw, pair_label, "01 raw t file")
        )

        print("\nStep 2: Restrict to outgoing rotation groups")
        df0_morg = restrict_to_morg(df0_raw)
        df1_morg = restrict_to_morg(df1_raw)

        morg_t_N = len(df0_morg)
        morg_t1_N = len(df1_morg)

        characteristics_rows.append(
            summarize_sample(df0_morg, pair_label, "02 t file after MIS 4/8 restriction")
        )

        print("\nStep 3: Naive merge")
        merged_naive = create_panel(df0_morg, df1_morg)

        if merged_naive.empty:
            print(f"No matches for {y0}-{y1}")
            attrition_rows.append({
                "pair": pair_label,
                "raw_t_N": raw_t_N,
                "raw_t1_N": raw_t1_N,
                "after_mis_t_N": morg_t_N,
                "after_mis_t1_N": morg_t1_N,
                "naive_merge_N": 0,
                "after_sex_race_filter_N": 0,
                "sex_race_rejected_N": np.nan,
            })
            continue

        naive_N = len(merged_naive)
        print(f"Total naive matches: {naive_N:,}")

        characteristics_rows.append(
            summarize_sample(merged_naive, pair_label, "03 naive merged sample")
        )

        # Save naive merged file too, so you can audit later
        naive_out_file = OUTPUT_DIR / f"naive_merged_morg_{str(y0)[-2:]}{str(y1)[-2:]}.csv"
        merged_naive.to_csv(naive_out_file, index=False)
        print(f"Saved naive merge: {naive_out_file}")

        print("\nStep 4: Apply sex/race consistency filter")
        valid, invalid = apply_sra_filter(merged_naive)

        valid_N = len(valid)
        invalid_N = len(invalid)

        print(f"Valid matches after sex/race filter: {valid_N:,}")
        print(f"Rejected by sex/race filter: {invalid_N:,}")

        characteristics_rows.append(
            summarize_sample(valid, pair_label, "04 after sex/race filter")
        )

        if invalid_N > 0:
            characteristics_rows.append(
                summarize_sample(invalid, pair_label, "04b rejected by sex/race filter")
            )

        # Save rejected rows too, helpful for audit
        invalid_out_file = OUTPUT_DIR / f"rejected_sex_race_morg_{str(y0)[-2:]}{str(y1)[-2:]}.csv"
        invalid.to_csv(invalid_out_file, index=False)
        print(f"Saved rejected matches: {invalid_out_file}")

        # Your original final output
        out_file = OUTPUT_DIR / f"merged_morg_{str(y0)[-2:]}{str(y1)[-2:]}.csv"
        valid.to_csv(out_file, index=False)
        print(f"Saved valid final merged sample: {out_file}")

        attrition_rows.append({
            "pair": pair_label,

            "raw_t_N": raw_t_N,
            "raw_t1_N": raw_t1_N,

            "after_mis_t_N": morg_t_N,
            "after_mis_t1_N": morg_t1_N,

            "naive_merge_N": naive_N,
            "after_sex_race_filter_N": valid_N,
            "sex_race_rejected_N": invalid_N,

            "lost_raw_t_to_mis_N": raw_t_N - morg_t_N,
            "lost_mis_to_naive_merge_N": morg_t_N - naive_N,
            "lost_naive_to_sex_race_filter_N": naive_N - valid_N,
            "lost_raw_t_to_final_N": raw_t_N - valid_N,

            "mis_retention_rate_vs_raw_t": morg_t_N / raw_t_N if raw_t_N > 0 else np.nan,
            "naive_match_rate_vs_mis_t": naive_N / morg_t_N if morg_t_N > 0 else np.nan,
            "sex_race_retention_rate_vs_naive": valid_N / naive_N if naive_N > 0 else np.nan,
            "final_retention_rate_vs_raw_t": valid_N / raw_t_N if raw_t_N > 0 else np.nan,
        })

    # ------------------------------------------------------------
    # Build and save summary tables
    # ------------------------------------------------------------

    attrition_table = pd.DataFrame(attrition_rows)
    characteristics_table = pd.DataFrame(characteristics_rows)

    # Add percent versions
    pct_cols = [
        "mis_retention_rate_vs_raw_t",
        "naive_match_rate_vs_mis_t",
        "sex_race_retention_rate_vs_naive",
        "final_retention_rate_vs_raw_t",
    ]

    for col in pct_cols:
        if col in attrition_table.columns:
            attrition_table[col + "_pct"] = 100 * attrition_table[col]

    attrition_out = OUTPUT_DIR / "merge_attrition_raw_mis_naive_sexrace_final.csv"
    characteristics_out = OUTPUT_DIR / "sample_characteristics_by_merge_stage.csv"

    attrition_table.to_csv(attrition_out, index=False)
    characteristics_table.to_csv(characteristics_out, index=False)

    print("\nDONE.")
    print(f"Saved attrition table: {attrition_out}")
    print(f"Saved characteristics table: {characteristics_out}")

    display(attrition_table)
    display(characteristics_table)


if __name__ == "__main__":
    main()