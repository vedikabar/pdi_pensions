# ------------------------------------------------------------
# Convert CPS MORG .dta files (morg08.dta ... morg17.dta)
# to CSV format. No modifications -- pure format conversion.
# ------------------------------------------------------------

from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/morg")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEAR_SUFFIXES = [f"{y:02d}" for y in range(8, 18)]  # 08 ... 17

# Optional faster reader
try:
    import pyreadstat
    USE_PYREADSTAT = True
except ImportError:
    USE_PYREADSTAT = False

for y in YEAR_SUFFIXES:
    dta_path = RAW_DIR / f"morg{y}.dta"
    csv_path = OUTPUT_DIR / f"morg{y}.csv"

    if not dta_path.exists():
        print(f"[WARNING] File not found: {dta_path}")
        continue

    print(f"[INFO] Reading {dta_path}")

    if USE_PYREADSTAT:
        df, meta = pyreadstat.read_dta(dta_path)
    else:
        df = pd.read_stata(dta_path, convert_categoricals=False)

    print(f"[INFO] Writing {csv_path}")
    df.to_csv(csv_path, index=False)

print("[DONE] Conversion complete.")
