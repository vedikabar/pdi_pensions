import pandas as pd

INPUT_FILE = "/Users/vedikabaradwaj/pdi_pensions/data/merged/merged_morg_0809.csv"
OUTPUT_FILE = "analytic_sample_0809_il_public_t.csv"

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(INPUT_FILE, low_memory=False)
df.columns = df.columns.str.lower().str.strip()

print(f"Loaded {len(df):,} rows")

# -----------------------------
# Required columns
# -----------------------------
required_cols = [
    "sex_t", "sex_t1",
    "race_t", "race_t1",
    "stfips_t", "stfips_t1",
    "class94_t", "class94_t1",
    "lfsr94_t1"
]

missing = [col for col in required_cols if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# -----------------------------
# Clean numeric columns
# -----------------------------
for col in ["stfips_t", "stfips_t1", "class94_t", "class94_t1", "lfsr94_t1"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -----------------------------
# 1. Sex + race consistency
# -----------------------------
df = df[
    (df["sex_t"] == df["sex_t1"]) &
    (df["race_t"] == df["race_t1"])
].copy()

print(f"After sex/race filter: {len(df):,}")

# -----------------------------
# 2. Illinois only
# -----------------------------
df = df[
    (df["stfips_t"] == 17) &
    (df["stfips_t1"] == 17)
].copy()

print(f"After Illinois filter: {len(df):,}")

# -----------------------------
# 3. Public at time t ONLY
# -----------------------------
PUBLIC_CODES = [1, 2, 3]

df = df[df["class94_t"].isin(PUBLIC_CODES)].copy()

print(f"After public-at-t filter: {len(df):,}")

# -----------------------------
# (Optional but VERY useful)
# Create outcome variables
# -----------------------------
PRIVATE_CODES = [4, 5]          # private for-profit / non-profit, wage & salary only
SELF_EMPLOYED_CODES = [6, 7]    # self-employed, incorporated / unincorporated
RETIRED_LFSR94 = 5              # lfsr94 code: "not in labor force - retired"

# stayed in public
df["stayed_public"] = df["class94_t1"].isin(PUBLIC_CODES)

# moved to a genuine private-sector wage/salary job. Deliberately excludes
# self-employed (the CPS MORG codebook warns against using self-employed
# earnings data) so this isn't conflated with moved_self_employed below.
df["moved_private"] = df["class94_t1"].isin(PRIVATE_CODES)

# became self-employed
df["moved_self_employed"] = df["class94_t1"].isin(SELF_EMPLOYED_CODES)

# class94 is only populated for people who are employed, so a missing value
# at t1 means unemployed, retired, or otherwise out of the labor force --
# NOT the same thing as having taken a private-sector job.
df["not_employed_t1"] = df["class94_t1"].isna()

# retired specifically (the outcome most directly relevant to a pension
# study), using the labor force status recode rather than class94
df["retired_t1"] = df["lfsr94_t1"] == RETIRED_LFSR94

# exited public: kept for backward compatibility. NOTE this bundles
# moved_private, moved_self_employed, AND not_employed_t1 together -- about
# a third of "exited" cases in past samples were actually not_employed_t1,
# not a move to a private job. Use the variables above when that
# distinction matters.
df["exited_public"] = (
    df["class94_t"].isin(PUBLIC_CODES) &
    ~df["class94_t1"].isin(PUBLIC_CODES)
)

# switched sector (any change)
df["switched_sector"] = df["class94_t"] != df["class94_t1"]

# -----------------------------
# Save
# -----------------------------
df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved to {OUTPUT_FILE}")