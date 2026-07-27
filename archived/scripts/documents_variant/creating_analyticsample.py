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
    "class94_t", "class94_t1"
]

missing = [col for col in required_cols if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# -----------------------------
# Clean numeric columns
# -----------------------------
for col in ["stfips_t", "stfips_t1", "class94_t", "class94_t1"]:
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

# stayed in public
df["stayed_public"] = df["class94_t1"].isin(PUBLIC_CODES)

# exited public
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