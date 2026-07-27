import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIG — CHANGE Y0/Y1 EACH RUN (this script processes one pair at a time;
# it is not looped like 03_merge_years_loop.py / 04_build_analytic_sample.py)
# --------------------------------------------------
PROJECT_DIR = Path("/Users/vedikabaradwaj/pdi_pensions")
MATCH_DIR = PROJECT_DIR / "data" / "match"     # input: output of 03_merge_years_loop.py
OUTPUT_DIR = PROJECT_DIR / "data" / "analytic_samples"  # writes to */retention and */recruitment below

Y0 = 2016
Y1 = 2017
INPUT_FILE = MATCH_DIR / f"match_morg_{str(Y0)[-2:]}{str(Y1)[-2:]}.csv"

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

STATE_LOCAL_CODES = [2, 3]
ALL_PUBLIC_CODES  = [1, 2, 3]
PRIVATE_CODES     = [4, 5, 6, 7, 8]

STATE_FIPS = {
    "illinois": 17,
    "pennsylvania": 42,
    "new_york": 36,
    "indiana": 18,
}

TREATMENT_FIPS = STATE_FIPS["illinois"]
ALL_FIPS = set(STATE_FIPS.values())

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def pair_tag(y0, y1):
    return f"{str(y0)[-2:]}{str(y1)[-2:]}"

def validate_columns(df):
    required_cols = [
        "sex_t", "sex_t1",
        "race_t", "race_t1",
        "stfips_t",
        "class94_t", "class94_t1",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def load_and_clean():
    print(f"\nProcessing file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, low_memory=False)
    df.columns = df.columns.str.lower().str.strip()

    validate_columns(df)

    for col in ["stfips_t", "class94_t", "class94_t1", "sex_t", "sex_t1", "race_t", "race_t1"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"Loaded rows: {len(df):,}")
    return df

def filter_sex_race(df):
    mask = (df["sex_t"] == df["sex_t1"]) & (df["race_t"] == df["race_t1"])
    out = df[mask].copy()
    print(f"After sex/race filter: {len(out):,}")
    return out

def add_state_label(df):
    inv = {v: k for k, v in STATE_FIPS.items()}
    df["state"] = df["stfips_t"].map(inv)
    df["illinois"] = (df["stfips_t"] == TREATMENT_FIPS).astype(int)
    return df

# --------------------------------------------------
# RETENTION SAMPLE
# --------------------------------------------------

def build_retention_sample(df):
    df = df[df["stfips_t"].isin(ALL_FIPS)].copy()
    df = df[df["class94_t"].isin(STATE_LOCAL_CODES)].copy()

    df["year_t"] = Y0
    df["year_t1"] = Y1
    df["pair"] = f"{Y0}-{Y1}"

    df["stayed_state_local"] = df["class94_t1"].isin(STATE_LOCAL_CODES).astype(int)
    df["exited_state_local"] = (~df["class94_t1"].isin(STATE_LOCAL_CODES)).astype(int)

    df["moved_to_federal"] = (df["class94_t1"] == 1).astype(int)
    df["moved_to_private"] = df["class94_t1"].isin(PRIVATE_CODES).astype(int)

    df["analytic_sample"] = "retention"
    return df

# --------------------------------------------------
# RECRUITMENT SAMPLE
# --------------------------------------------------

def build_recruitment_sample(df):
    df = df[df["stfips_t"].isin(ALL_FIPS)].copy()
    df = df[~df["class94_t"].isin(STATE_LOCAL_CODES)].copy()

    df["year_t"] = Y0
    df["year_t1"] = Y1
    df["pair"] = f"{Y0}-{Y1}"

    df["joined_state_local"] = df["class94_t1"].isin(STATE_LOCAL_CODES).astype(int)

    df["from_federal"] = (df["class94_t"] == 1).astype(int)
    df["from_private"] = df["class94_t"].isin(PRIVATE_CODES).astype(int)

    df["analytic_sample"] = "recruitment"
    return df

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    df = load_and_clean()
    df = filter_sex_race(df)
    df = add_state_label(df)

    tag = pair_tag(Y0, Y1)

    (OUTPUT_DIR / "retention").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "recruitment").mkdir(parents=True, exist_ok=True)

    df_ret = build_retention_sample(df.copy())
    out_ret = OUTPUT_DIR / "retention" / f"analytic_sample_{tag}_retention.csv"
    df_ret.to_csv(out_ret, index=False)
    print(f"Saved retention → {out_ret}")

    df_rec = build_recruitment_sample(df.copy())
    out_rec = OUTPUT_DIR / "recruitment" / f"analytic_sample_{tag}_recruitment.csv"
    df_rec.to_csv(out_rec, index=False)
    print(f"Saved recruitment → {out_rec}")

    print("\nDone.")

if __name__ == "__main__":
    main()