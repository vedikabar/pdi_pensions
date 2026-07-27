import pandas as pd
from pathlib import Path

df = pd.read_csv(Path.home() / "Documents/pdi_pensions/data/csv/morg08.csv", 
                 nrows=5000, low_memory=False)
df.columns = df.columns.str.lower().str.strip()

# 1. Find the class-of-worker column
print("Class-of-worker candidates:")
for c in df.columns:
    if any(x in c for x in ['class','cls','sector','gov']):
        print(f"  {c}: unique values = {sorted(df[c].dropna().unique().tolist())}")

# 2. Find weight column and check its scale
print("\nWeight column check:")
w = df['weight'] if 'weight' in df.columns else None
if w is not None:
    print(f"  weight: min={w.min():.0f}, max={w.max():.0f}, mean={w.mean():.0f}")
    print(f"  Divided by 1000: min={w.min()/1000:.1f}, max={w.max()/1000:.1f}")

# 3. What does a few rows look like for employment vars
emp_cols = [c for c in df.columns if any(x in c for x in 
            ['class','lfstat','emp','sector','ind','occ','earn','weight'])]
print(f"\nEmployment-related columns: {emp_cols}")
print(df[emp_cols[:8]].head(10).to_string())