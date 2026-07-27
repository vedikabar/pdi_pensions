import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
# Put this script in the same folder as your merged CSVs
DATA_DIR = Path(".")

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

PUBLIC_CODES = [1, 2, 3]        # federal, state, local
PRIVATE_CODES = [4, 5]          # private for-profit / non-profit, wage & salary only
SELF_EMPLOYED_CODES = [6, 7]    # self-employed, incorporated / unincorporated
RETIRED_LFSR94 = 5              # lfsr94 code: "not in labor force - retired"
ILLINOIS_FIPS = 17


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def pair_tag(y0: int, y1: int) -> str:
    return f"{str(y0)[-2:]}{str(y1)[-2:]}"


def input_filename(y0: int, y1: int) -> str:
    # Change this if your filenames are different
    return f"/Users/vedikabaradwaj/pdi_pensions/data/csv/merged_morg_{pair_tag(y0, y1)}.csv"


def output_filename(y0: int, y1: int) -> str:
    return f"analytic_sample_{pair_tag(y0, y1)}_il_public_t.csv"


def validate_columns(df: pd.DataFrame, fname: str) -> None:
    required_cols = [
        "sex_t", "sex_t1",
        "race_t", "race_t1",
        "stfips_t", "stfips_t1",
        "class94_t", "class94_t1",
        "lfsr94_t1"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"{fname} is missing required columns: {missing}")


def process_pair(y0: int, y1: int) -> None:
    in_path = DATA_DIR / input_filename(y0, y1)
    out_path = DATA_DIR / output_filename(y0, y1)

    if not in_path.exists():
        print(f"Skipping {y0}-{y1}: file not found -> {in_path.name}")
        return

    print(f"\n{'=' * 70}")
    print(f"Processing {y0}-{y1}: {in_path.name}")
    print(f"{'=' * 70}")

    df = pd.read_csv(in_path, low_memory=False)
    df.columns = df.columns.str.lower().str.strip()

    validate_columns(df, in_path.name)

    for col in ["stfips_t", "stfips_t1", "class94_t", "class94_t1", "lfsr94_t1"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    start_n = len(df)
    print(f"Loaded rows: {start_n:,}")

    # 1. Sex/race-consistent matches
    sr_mask = (
        (df["sex_t"] == df["sex_t1"]) &
        (df["race_t"] == df["race_t1"])
    )
    df = df[sr_mask].copy()
    n_sr = len(df)
    print(f"After sex/race filter: {n_sr:,} kept, {start_n - n_sr:,} dropped")

    # 2. Illinois at baseline (time t only)
    il_mask = df["stfips_t"] == ILLINOIS_FIPS
    df = df[il_mask].copy()
    n_il = len(df)
    print(f"After Illinois-at-t filter: {n_il:,} kept, {n_sr - n_il:,} dropped")

    # 3. Public employee at baseline (time t only)
    public_t_mask = df["class94_t"].isin(PUBLIC_CODES)
    df = df[public_t_mask].copy()
    n_final = len(df)
    print(f"After public-at-t filter: {n_final:,} kept, {n_il - n_final:,} dropped")

    # --------------------------------------------------
    # Create useful outcome variables
    # --------------------------------------------------
    df["year_t"] = y0
    df["year_t1"] = y1
    df["pair"] = f"{y0}-{y1}"

    # Whether still public in t+1
    df["stayed_public"] = df["class94_t1"].isin(PUBLIC_CODES)

    # Moved to a genuine private-sector wage/salary job. Deliberately
    # excludes self-employed (the CPS MORG codebook warns against using
    # self-employed earnings data) so this isn't conflated with
    # moved_self_employed below.
    df["moved_private"] = df["class94_t1"].isin(PRIVATE_CODES)

    # Became self-employed
    df["moved_self_employed"] = df["class94_t1"].isin(SELF_EMPLOYED_CODES)

    # class94 is only populated for people who are employed, so a missing
    # value at t1 means unemployed, retired, or otherwise out of the labor
    # force -- NOT the same thing as having taken a private-sector job.
    df["not_employed_t1"] = df["class94_t1"].isna()

    # Retired specifically (the outcome most directly relevant to a pension
    # study), using the labor force status recode rather than class94.
    df["retired_t1"] = df["lfsr94_t1"] == RETIRED_LFSR94

    # Whether left public by t+1: kept for backward compatibility. NOTE this
    # bundles moved_private, moved_self_employed, AND not_employed_t1
    # together -- about a third of "exited" cases in past samples were
    # actually not_employed_t1, not a move to a private job. Use the
    # variables above when that distinction matters.
    df["exited_public"] = ~df["class94_t1"].isin(PUBLIC_CODES)

    # Whether changed class94 category
    df["switched_class94"] = df["class94_t"] != df["class94_t1"]

    # Optional sample flag
    df["analytic_sample"] = 1

    # Save
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path.name} ({n_final:,} rows)")


def main():
    for y0, y1 in YEAR_PAIRS:
        process_pair(y0, y1)

    print(f"\nDone with all available year-pair files.")


if __name__ == "__main__":
    main()