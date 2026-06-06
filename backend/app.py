import os, sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from pathlib import Path

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATA_PATH = Path(__file__).parent.parent / "data" / "clean_faults.csv"

def get_df():
    if not DATA_PATH.exists():
        
        import numpy as np
        print("⚠️ Temizlenmiş veri bulunamadı! Test verisi üretiliyor...")
        brands = ['BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Ford', 'Renault']
        models = ['Series 3', 'C-Class', 'A4', 'Golf', 'Focus', 'Clio']
        categories = ['Motor', 'Fren', 'Elektrik', 'Şanzıman', 'Süspansiyon']
        parts = ['Buji', 'Balata', 'Alternatör', 'Debriyaj Seti', 'Amortisör']
        sources = ['Sensör', 'Yazılım', 'Mekanik']
        status = ['Tamamlandı', 'Beklemede', 'Tamirde']
        
        np.random.seed(42)
        n = 500
        df = pd.DataFrame({
            'brand': np.random.choice(brands, n),
            'model': np.random.choice(models, n),
            'fault_category': np.random.choice(categories, n),
            'part': np.random.choice(parts, n),
            'automation_source': np.random.choice(sources, n),
            'status': np.random.choice(status, n),
            'repair_hours': np.random.uniform(1.0, 8.0, n).round(1),
            'cost': np.random.uniform(200, 3000, n).round(2),
            'year': np.random.choice([2025, 2026], n),
            'month': np.random.randint(1, 13, n)
        })
        DATA_PATH.parent.mkdir(exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "database": DATA_PATH.exists()})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    df = get_df()
    total_faults = len(df)
    total_cost = float(df['cost'].sum())
    avg_repair_time = float(df['repair_hours'].mean())
    # Basit bir MTBF simülasyonu (çalışma saati / arıza sayısı)
    mtbf = round((total_faults * 150) / max(total_faults, 1), 1)
    
    return jsonify({
        "total_faults": total_faults,
        "total_cost": round(total_cost, 2),
        "avg_repair_time": round(avg_repair_time, 1),
        "mtbf_hours": mtbf
    })

@app.route('/api/parts', methods=['GET'])
def get_parts():
    df = get_df()
    res = df.groupby('fault_category').size().to_dict()
    return jsonify(res)

@app.route('/api/automation', methods=['GET'])
def get_automation():
    df = get_df()
    res = df.groupby('automation_source').size().to_dict()
    return jsonify(res)

@app.route('/api/trends', methods=['GET'])
def get_trends():
    df = get_df()
    # Aylık trend analizi
    res = df.groupby('month').size().to_dict()
    # Eksik ayları 0 ile dolduralım
    full_res = {str(m): res.get(m, 0) for m in range(1, 13)}
    return jsonify(full_res)

@app.route('/api/correlation', methods=['GET'])
def get_correlation():
    df = get_df()
    # Süre ve Maliyet korelasyonu için örnek veri noktaları
    sample = df.sample(min(100, len(df))).to_dict(orient='records')
    return jsonify(sample)

@app.route('/api/performance', methods=['GET'])
def get_performance():
    df = get_df()
    # Marka bazlı performans skoru (Düşük maliyet ve süre = Yüksek Skor)
    brand_stats = df.groupby('brand').agg({'cost': 'mean', 'repair_hours': 'mean'}).reset_index()
    res = []
    for _, row in brand_stats.iterrows():
        # 100 üzerinden basit bir skorlama algoritması
        score = max(10, min(100, int(100 - (row['cost'] / 50) - (row['repair_hours'] * 2))))
        res.append({"brand": row['brand'], "score": score})
    return jsonify(res)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    df = get_df()
    # Yüksek maliyetli veya uzun süren kritik arızaları filtrele
    critical = df[df['cost'] > 2000].head(5).to_dict(orient='records')
    return jsonify(critical)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)