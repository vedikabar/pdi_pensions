# ------------------------------------------------------------
# Convert specific CPS MORG .dta files to CSV format
# (file-by-file conversion using explicit file paths)
# ------------------------------------------------------------

from pathlib import Path
import pandas as pd

# List of specific .dta file paths (EDIT THIS)
DTA_FILES = [
    Path("data/raw/morg16.dta"),
    Path("data/raw/morg17.dta"),
    # add more as needed
]

# Output directory
OUTPUT_DIR = Path("data/csv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Optional faster reader
try:
    import pyreadstat
    USE_PYREADSTAT = True
except ImportError:
    USE_PYREADSTAT = False

# ------------------------------------------------------------
# Process each file individually
# ------------------------------------------------------------
for dta_path in DTA_FILES:

    if not dta_path.exists():
        print(f"[WARNING] File not found: {dta_path}")
        continue

    # Create output filename dynamically
    csv_path = OUTPUT_DIR / f"{dta_path.stem}.csv"

    print(f"[INFO] Reading {dta_path}")

    if USE_PYREADSTAT:
        df, meta = pyreadstat.read_dta(dta_path)
    else:
        df = pd.read_stata(dta_path, convert_categoricals=False)

    print(f"[INFO] Writing {csv_path}")
    df.to_csv(csv_path, index=False)

print("[DONE] Conversion complete.")