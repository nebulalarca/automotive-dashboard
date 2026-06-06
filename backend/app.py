from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_PATH = Path(__file__).parent.parent / "data" / "clean_faults.csv"

def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates=["date"])
    return _generate_sample_data()

def _generate_sample_data():
    import random
    random.seed(42)
    BRANDS = ["BMW","Mercedes","Toyota","Volkswagen","Ford","Honda","Audi","Hyundai"]
    MODELS = {
        "BMW":["3 Serisi","5 Serisi","X5"],
        "Mercedes":["C Serisi","E Serisi","GLE"],
        "Toyota":["Corolla","RAV4","Camry"],
        "Volkswagen":["Golf","Passat","Tiguan"],
        "Ford":["Focus","Mondeo","Explorer"],
        "Honda":["Civic","CR-V","Accord"],
        "Audi":["A4","A6","Q5"],
        "Hyundai":["i20","Tucson","Elantra"],
    }
    FAULTS = ["Motor","Elektrik","Fren Sistemi","Şanzıman","Süspansiyon","Yakıt Sistemi"]
    PARTS  = ["Motor Bloğu","Alternator","Fren Balatası","Vites Kutusu","Amortisör","Enjektör"]
    AUTOS  = ["OBD-II Sensör","ABS Modülü","ECU Yazılım","TPMS","Park Sensörü","Lane Assist"]
    STATUS = ["repaired","repaired","repaired","pending","open","resolved"]
    rows = []
    for _ in range(3000):
        brand = random.choice(BRANDS)
        rows.append({
            "brand": brand,
            "model": random.choice(MODELS[brand]),
            "fault_category": random.choice(FAULTS),
            "part": random.choice(PARTS),
            "automation_source": random.choice(AUTOS),
            "status": random.choice(STATUS),
            "repair_hours": round(random.uniform(1,6),1),
            "cost": round(random.uniform(500,15000),0),
            "date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=random.randint(0,364)),
            "year": 2024,
            "month": random.randint(1,12),
        })
    return pd.DataFrame(rows)

def apply_filters(df):
    year  = request.args.get("year",  type=int)
    brand = request.args.get("brand", type=str)
    if year  and "year"  in df.columns: df = df[df["year"] == year]
    if brand and brand != "all" and "brand" in df.columns: df = df[df["brand"] == brand]
    return df

@app.route("/api/health")
def health():
    df = load_data()
    return jsonify({"status": "ok", "records": len(df), "timestamp": datetime.now().isoformat()})

@app.route("/api/kpis")
def kpis():
    df = apply_filters(load_data())
    total = len(df)
    repaired = df[df["status"].isin(["repaired","resolved"])]
    repair_rate = round(len(repaired)/total*100,1) if total else 0
    avg_hours = round(df["repair_hours"].mean(),1) if total else 0
    avg_cost  = round(df["cost"].mean(),0) if total else 0
    days = (df["date"].max()-df["date"].min()).days if "date" in df.columns and total > 1 else 1
    mtbf = round(days/total,0) if total else 0
    active = len(df[df["status"].isin(["open","pending"])])
    return jsonify([
        {"label":"Toplam Arıza",        "value":f"{total:,}",       "delta":"+4.2%",   "trend":"up",   "color":"#E03E3E","barW":f"{min(total//50,100)}%"},
        {"label":"Tamir Tamamlama",     "value":f"%{repair_rate}",  "delta":"+1.1%",   "trend":"good", "color":"#2D9B6F","barW":f"{repair_rate}%"},
        {"label":"Ort. Tamir Süresi",   "value":f"{avg_hours} sa",  "delta":"−0.3 sa", "trend":"good", "color":"#2C4FA3","barW":f"{min(int(avg_hours*10),100)}%"},
        {"label":"MTBF Ortalaması",     "value":f"{int(mtbf)} gün", "delta":"+5 gün",  "trend":"good", "color":"#2D9B6F","barW":f"{min(int(mtbf),100)}%"},
        {"label":"Ort. Tamir Maliyeti", "value":f"₺{int(avg_cost):,}","delta":"+8.1%","trend":"up",   "color":"#C9B99A","barW":"62%"},
        {"label":"Aktif Alarm",         "value":str(active),        "delta":"Açık kayıt","trend":"up", "color":"#E03E3E","barW":"24%"},
        {"label":"Toplam Marka",        "value":str(df["brand"].nunique()),"delta":"Marka","trend":"neu","color":"#8B6FC1","barW":"80%"},
        {"label":"Veri Kaynağı",        "value":"Kaggle",           "delta":"CSV aktif","trend":"neu", "color":"#1E2D6B","barW":"100%"},
    ])

@app.route("/api/trend")
def trend():
    df = apply_filters(load_data())
    MONTHS = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"]
    faults  = df.groupby("month").size().reindex(range(1,13),fill_value=0).tolist()
    repaired = df[df["status"].isin(["repaired","resolved"])]
    repairs = repaired.groupby("month").size().reindex(range(1,13),fill_value=0).tolist()
    return jsonify({"months":MONTHS,"faults":faults,"repairs":repairs})

@app.route("/api/categories")
def categories():
    df = apply_filters(load_data())
    COLORS = ["#E03E3E","#2C4FA3","#C9B99A","#8B6FC1","#1E2D6B","#2D9B6F","#888780"]
    counts = df["fault_category"].value_counts().head(7)
    total  = counts.sum()
    return jsonify([{"name":k,"pct":round(v/total*100,1),"color":COLORS[i%len(COLORS)]} for i,(k,v) in enumerate(counts.items())])

@app.route("/api/brands")
def brands():
    df = apply_filters(load_data())
    COLORS = ["#E03E3E","#2C4FA3","#2D9B6F","#C9B99A","#8B6FC1","#1E2D6B","#C47A1A","#888780"]
    counts = df["brand"].value_counts().head(8)
    result = []
    for i,(brand,cnt) in enumerate(counts.items()):
        sub = df[df["brand"]==brand]
        rep = sub[sub["status"].isin(["repaired","resolved"])]
        rate = round(len(rep)/len(sub)*100,1) if len(sub) else 0
        result.append({"name":brand,"faults":int(cnt),"repairRate":rate,"color":COLORS[i%len(COLORS)],"segment":"premium" if brand in ["BMW","Mercedes","Audi","Volvo"] else "mid"})
    return jsonify(result)

@app.route("/api/parts")
def parts():
    df = apply_filters(load_data())
    ICONS  = ["⚙️","⚡","🛞","🔧","🔩","⛽"]
    COLORS = ["#E03E3E","#2C4FA3","#C9B99A","#8B6FC1","#2D9B6F","#1E2D6B"]
    BGS    = ["#FDEAEA","#E8EDF8","#F5F0E8","#EDE8F8","#E2F5ED","#E8EDF8"]
    counts = df["part"].value_counts().head(6)
    total  = counts.sum()
    return jsonify([{"name":k,"count":int(v),"pct":round(v/total*100,1),"icon":ICONS[i%len(ICONS)],"color":COLORS[i%len(COLORS)],"bg":BGS[i%len(BGS)]} for i,(k,v) in enumerate(counts.items())])

@app.route("/api/automations")
def automations():
    df = apply_filters(load_data())
    counts = df["automation_source"].value_counts().head(6)
    total  = counts.sum()
    def sev(i,v,t):
        p = v/t
        if i==0 or p>0.25: return "critical"
        if p>0.12: return "warning"
        return "info"
    return jsonify([{"name":k,"count":int(v),"severity":sev(i,v,total)} for i,(k,v) in enumerate(counts.items())])

@app.route("/api/alarms")
def alarms():
    df = apply_filters(load_data())
    COLORS = {"critical":"#E03E3E","warning":"#C47A1A","info":"#2C4FA3"}
    open_df = df[df["status"].isin(["open","pending"])].head(10)
    if open_df.empty: open_df = df.head(6)
    def sev(s):
        if s in ["open","critical"]: return "critical"
        if s in ["pending"]: return "warning"
        return "info"
    result = []
    for _,row in open_df.iterrows():
        s = sev(str(row.get("status","")))
        result.append({"brand":f"{row.get('brand','-')} {row.get('model','')}".strip(),"msg":row.get("fault_category","Arıza"),"part":row.get("part","—"),"time":str(row.get("date",""))[:10],"severity":s,"color":COLORS[s]})
    return jsonify(result)

@app.route("/api/models")
def models():
    df = apply_filters(load_data())
    SEGMENT = {"BMW":"Premium","Mercedes":"Premium","Audi":"Premium","Volvo":"Premium"}
    grp = df.groupby(["brand","model"]).agg(faults=("brand","count"),avg_hours=("repair_hours","mean"),avg_cost=("cost","mean")).reset_index()
    days = (df["date"].max()-df["date"].min()).days if "date" in df.columns else 365
    result = []
    for _,row in grp.iterrows():
        sub = df[(df["brand"]==row["brand"])&(df["model"]==row["model"])]
        rep = sub[sub["status"].isin(["repaired","resolved"])]
        rate = round(len(rep)/len(sub)*100,1) if len(sub) else 90
        mtbf = max(int(days/len(sub)) if len(sub) else 60, 5)
        result.append({"brand":row["brand"],"model":row["model"],"seg":SEGMENT.get(row["brand"],"Orta"),"faults":int(row["faults"]),"repair":rate,"hrs":round(float(row["avg_hours"]),1),"mtbf":mtbf,"cost":int(row["avg_cost"])})
    result.sort(key=lambda x: x["faults"],reverse=True)
    return jsonify(result[:20])

@app.route("/api/repair-cost")
def repair_cost():
    df = apply_filters(load_data())
    COLORS = ["#E03E3E","#2C4FA3","#2D9B6F","#C9B99A","#8B6FC1","#1E2D6B","#C47A1A","#888780"]
    grp = df.groupby("brand").agg(avg_hours=("repair_hours","mean"),avg_cost=("cost","mean")).reset_index().sort_values("avg_cost",ascending=False).head(8)
    return jsonify({"brands":grp["brand"].tolist(),"hours":[round(h,1) for h in grp["avg_hours"]],"costs":[int(c) for c in grp["avg_cost"]],"colors":COLORS[:len(grp)]})

if __name__ == "__main__":
    print("\n🚗 Automotive Dashboard API başlatılıyor...")
    print("   http://localhost:5001/api/health\n")
    app.run(debug=True, host="0.0.0.0", port=5001)