import os, json, sys
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DATASET = "aryan208/motor-vehicle-repair-and-towing-dataset"

def download():
    print(f"[1/3] Kaggle'dan indiriliyor: {DATASET}")
    os.system(
        f"kaggle datasets download -d {DATASET} "
        f"--unzip -p {DATA_DIR} --quiet"
    )
    csvs = list(DATA_DIR.glob("*.csv"))
    if not csvs:
        print("HATA: CSV bulunamadı. kaggle.json doğru mu?")
        sys.exit(1)
    print(f"      İndirilen: {[f.name for f in csvs]}")
    return csvs[0]

def clean(path):
    print(f"[2/3] Temizleniyor: {path.name}")
    df = pd.read_csv(path)
    print(f"      Sütunlar: {list(df.columns)}")
    print(f"      Satır sayısı: {len(df)}")

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[\s\-/]+", "_", regex=True)
    )

    COLUMN_MAP = {
        "vehicle_make": "brand", "make": "brand",
        "vehicle_model": "model", "model_name": "model",
        "fault_type": "fault_category", "issue_type": "fault_category",
        "repair_type": "fault_category", "service_type": "fault_category",
        "part_name": "part", "component": "part", "failed_part": "part",
        "system": "automation_source", "sensor_type": "automation_source",
        "repair_status": "status", "resolved": "status",
        "repair_time": "repair_hours", "labor_hours": "repair_hours",
        "repair_cost": "cost", "total_cost": "cost",
        "repair_date": "date", "service_date": "date",
    }
    df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns}, inplace=True)

    REQUIRED = ["brand","model","fault_category","part",
                "automation_source","status","repair_hours","cost","date"]
    for col in REQUIRED:
        if col not in df.columns:
            print(f"      '{col}' sütunu yok, varsayılan eklendi")
            df[col] = "Unknown"

    df["repair_hours"] = pd.to_numeric(df["repair_hours"], errors="coerce").fillna(2.0)
    df["cost"]         = pd.to_numeric(df["cost"],         errors="coerce").fillna(500.0)
    df["date"]         = pd.to_datetime(df["date"],        errors="coerce")
    df["year"]         = df["date"].dt.year.fillna(2024).astype(int)
    df["month"]        = df["date"].dt.month.fillna(1).astype(int)

    df.dropna(subset=["brand","fault_category"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def save(df):
    print("[3/3] Kaydediliyor...")
    out = DATA_DIR / "clean_faults.csv"
    df.to_csv(out, index=False)
    print(f"      ✓ {len(df)} satır kaydedildi → {out}")

if __name__ == "__main__":
    csv_path = download()
    df       = clean(csv_path)
    save(df)
    print("\n Tamamlandı!")

 