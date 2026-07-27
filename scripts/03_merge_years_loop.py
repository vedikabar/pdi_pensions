from pathlib import Path
import sys
import pandas as pd


# -----------------------------
# CONFIG
# -----------------------------
PROJECT_DIR = Path("/Users/vedikabaradwaj/pdi_pensions")
MORG_DIR = PROJECT_DIR / "data" / "morg"           # input: per-year converted MORG files
NAIVE_MERGE_DIR = PROJECT_DIR / "data" / "naive_merge"  # output: raw two-year join, pre-filter
MATCH_DIR = PROJECT_DIR / "data" / "match"          # output: post S|R|A filter, validated panel

NAIVE_MERGE_DIR.mkdir(parents=True, exist_ok=True)
MATCH_DIR.mkdir(parents=True, exist_ok=True)

YEAR_PAIRS = [
    (2008, 2009),
    (2009, 2010),
    (2010, 2011),
    (2011, 2012),
    (2012, 2013),
    (2013, 2014),
    (2014, 2015),
    (2015, 2016),
    (2016, 2017),
]

# Where the per-pair attrition summary (see main()) gets written.
ATTRITION_OUT = MATCH_DIR / "merge_attrition_summary.csv"


# -----------------------------
# CORE FUNCTIONS
# -----------------------------
def load_morg(path: Path, year: int) -> pd.DataFrame:
    if not path.exists():
        print(f"Skipping {year}: file not found -> {path.name}")
        return None

    print(f"Loading {path} ...", flush=True)
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.lower().str.strip()

    # "age" and "stfips" are required here (not just sex/race) because
    # apply_sra_filter() needs age_t/age_t1 for the S|R|A check, and the
    # merge key below needs stfips for consistent state coding.
    required_basic = ["hhid", "hhnum", "lineno", "intmonth", "minsamp", "sex", "race", "age", "stfips"]
    missing = [c for c in required_basic if c not in df.columns]
    if missing:
        print(f"Skipping {path.name}: missing columns {missing}")
        return None

    # Merge key for state must use the same coding in every year. The raw
    # "state" column uses CPS's internal state numbering and is missing
    # entirely from the 2015 file; "stfips" (standard FIPS code) is present
    # with identical coding in every year 2008-2015, so it -- not "state" --
    # is used to join years. (Previously, a missing "state" column fell back
    # to "state = stfips", which silently mixed the two numbering schemes
    # across years and made every Illinois record fail to match in the
    # 2014-2015 pair, since IL=33 under the old scheme but IL=17 under FIPS.)
    df["state_key"] = df["stfips"]

    for col in ["hhid", "hhnum", "lineno", "intmonth", "state_key"]:
        df[col] = df[col].astype(str).str.strip()

    for col in ["minsamp", "sex", "race", "age"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year_file"] = year
    print(f"  {len(df):,} records loaded.")
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


def create_panel(df_t: pd.DataFrame, df_t1: pd.DataFrame) -> pd.DataFrame:
    merge_keys = ["hhid", "hhnum", "lineno", "intmonth", "state_key"]

    # Only MIS4 (year t) -> MIS8 (year t+1) is a real year-over-year link;
    # MIS8 is the outgoing group that leaves the sample for good, so there's
    # no household to find at MIS4 the following year (Madrian & Lefgren
    # 1999, NBER TWP 247, Sec. II). The old MIS8(t)->MIS4(t+1) branch has
    # been dropped since those "matches" were spurious.
    pairs = [
        (df_t[df_t["minsamp"] == 4].copy(), df_t1[df_t1["minsamp"] == 8].copy(), "MIS4_to_MIS8"),
    ]

    out = []
    for t_df, t1_df, label in pairs:
        t_df = t_df.rename(columns=build_rename_map(t_df, "_t", merge_keys))
        t1_df = t1_df.rename(columns=build_rename_map(t1_df, "_t1", merge_keys))

        merged = pd.merge(
            t_df,
            t1_df,
            on=merge_keys,
            how="inner",
        )
        merged["pair_type"] = label

        print(
            f"[{label}] {len(merged):,} matches "
            f"({len(t_df):,} vs {len(t1_df):,})"
        )
        out.append(merged)

    if not out:
        return pd.DataFrame()

    # state_key was only needed to make the join itself; the original
    # "state"/"stfips" columns (now state_t/state_t1, stfips_t/stfips_t1)
    # already carry that information through for downstream filtering.
    panel = pd.concat(out, ignore_index=True)
    return panel.drop(columns=["state_key"])


def apply_sra_filter(df: pd.DataFrame):
    # S|R|A criterion (Madrian & Lefgren 1999, NBER TWP 247, Sec. VII): reject
    # a naive match if sex differs, race differs, or age moved outside a
    # plausible one-year range. Using their "less restrictive" age band:
    # age_t1 - age_t must be in [-1, 3].
    sex_mismatch = df["sex_t"] != df["sex_t1"]
    race_mismatch = df["race_t"] != df["race_t1"]

    age_diff = df["age_t1"] - df["age_t"]
    age_mismatch = (age_diff < -1) | (age_diff > 3)

    invalid_mask = sex_mismatch | race_mismatch | age_mismatch

    valid = df.loc[~invalid_mask].copy()
    invalid = df.loc[invalid_mask].copy()

    return valid, invalid


# -----------------------------
# LOOP OVER YEARS
# -----------------------------
def main():
    attrition_rows = []

    for y0, y1 in YEAR_PAIRS:

        print("\n" + "=" * 80)
        print(f"PROCESSING {y0}-{y1}")
        print("=" * 80)

        # Build filenames like morg08.csv, morg09.csv
        f0 = MORG_DIR / f"morg{str(y0)[-2:]}.csv"
        f1 = MORG_DIR / f"morg{str(y1)[-2:]}.csv"

        df0 = load_morg(f0, y0)
        df1 = load_morg(f1, y1)

        if df0 is None or df1 is None:
            print(f"Skipping pair {y0}-{y1}")
            continue

        raw_t_n = len(df0)

        print("\nStep 2: Restrict to outgoing rotation groups")
        df0 = restrict_to_morg(df0)
        df1 = restrict_to_morg(df1)

        mis_t_n = len(df0)

        print("\nStep 3: Merge")
        merged = create_panel(df0, df1)

        if merged.empty:
            print(f"No matches for {y0}-{y1}")
            attrition_rows.append({
                "pair": f"{y0}-{y1}", "raw_t_n": raw_t_n, "after_mis_t_n": mis_t_n,
                "naive_merge_n": 0, "valid_sra_n": 0, "rejected_sra_n": 0,
            })
            continue

        naive_n = len(merged)
        print(f"Total matches: {naive_n:,}")

        naive_out_file = NAIVE_MERGE_DIR / f"naive_merge_morg_{str(y0)[-2:]}{str(y1)[-2:]}.csv"
        merged.to_csv(naive_out_file, index=False)
        print(f"Saved naive merge: {naive_out_file.name}")

        print("\nStep 4: Apply sex/race/age (S|R|A) filter")
        valid, invalid = apply_sra_filter(merged)

        valid_n, invalid_n = len(valid), len(invalid)
        print(f"Valid matches: {valid_n:,}")
        print(f"Rejected matches: {invalid_n:,}")

        # Save the validated ("matched") panel -- this is the file downstream
        # analytic-sample scripts should read from.
        out_file = MATCH_DIR / f"match_morg_{str(y0)[-2:]}{str(y1)[-2:]}.csv"
        valid.to_csv(out_file, index=False)
        print(f"Saved match: {out_file.name}")

        # Track how much sample is lost at each pipeline stage, so it's easy
        # to see e.g. whether a given year pair matched unusually poorly.
        attrition_rows.append({
            "pair": f"{y0}-{y1}",
            "raw_t_n": raw_t_n,
            "after_mis_t_n": mis_t_n,
            "naive_merge_n": naive_n,
            "valid_sra_n": valid_n,
            "rejected_sra_n": invalid_n,
            "naive_match_rate_vs_mis_t": naive_n / mis_t_n if mis_t_n else None,
            "sra_retention_rate_vs_naive": valid_n / naive_n if naive_n else None,
        })

    if attrition_rows:
        attrition_table = pd.DataFrame(attrition_rows)
        attrition_table.to_csv(ATTRITION_OUT, index=False)
        print(f"\nSaved per-pair attrition summary: {ATTRITION_OUT}")
        print(attrition_table.to_string(index=False))

    print("\nDONE with all year pairs.")


if __name__ == "__main__":
    main()