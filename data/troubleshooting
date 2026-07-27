from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "pdi_pensions" / "data" / "csv"

print("Looking in:", DATA_DIR)
print("Folder exists?", DATA_DIR.exists())

for name in ["morg15.csv", "morg16.csv", "morg17.csv"]:
    p = DATA_DIR / name
    print(name, "exists?", p.exists(), "| full path:", p)