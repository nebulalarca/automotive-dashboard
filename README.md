# 🚗 Automotive Fault & Repair Dashboard

Araç arıza ve tamir süreçlerini takip eden, Kaggle verisiyle beslenen Flask API + Vanilla JS dashboard.

## 📸 Özellikler
- 8 KPI kartı (arıza, tamir oranı, MTBF, maliyet)
- Aylık arıza & tamir trendi
- Hata kategorisi dağılımı
- Marka bazlı arıza analizi
- Parça kaynaklı hata takibi
- Otomasyon sistemi kaynak analizi
- Kritik alarm paneli
- Model bazlı performans & MTBF tablosu

## Kurulum

### 1. Bağımlılıkları kur
cd backend
pip install -r requirements.txt

### 2. Kaggle API key ayarla
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

### 3. Veriyi indir
python ingest.py

### 4. API'yı başlat
python app.py

### 5. Dashboard'u aç
cd ../frontend
npx serve .

## Teknoloji
- Python / Flask / pandas
- Vanilla JS / Chart.js
- Kaggle Dataset

## Veri Kaynağı
Kaggle — Motor Vehicle Repair & Towing Dataset

---
MIT License
