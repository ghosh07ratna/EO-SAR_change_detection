# EO–SAR Change Detection & Interpretation

## 📌 Project Overview
This project performs **multi-sensor (Sentinel‑1 SAR + Sentinel‑2 Optical) change detection and interpretation** across selected Regions of Interest (ROI).  
It demonstrates automated data acquisition, preprocessing (Python + QGIS + SNAP), and change analysis using both optical and radar imagery.

The results include change masks, visual outputs, and an analytical report describing findings, limitations, and interpretation.

---

## 🗂️ Directory Structure

```
EO-SAR-Change-Detection/
├── README.md
├── requirements.txt
│
├── data/
│   ├── RAW/   *large file to upload     
│   │       
│   │
│   └── ROI/
│
├── pre-processed_data/
│   ├── sentinel_1/
│   │   
│   │   
│   └── sentinel_2/
│       
│       
│
├── notebooks/
│   ├── change_detection_S1.ipynb
│   ├── change_detection_s2.ipynb
│   ├── data_acquisition_sentinel1.ipynb
│   ├── data_acquisition_sentinel2.ipynb
│   └── pre_process_merging_band_s2.ipynb
│
├── src/
│   ├── __init__.py
│   ├── change_detection_S1.py
│   ├── change_detection_s2.py
│   ├── data_acquisition_sentinel1.py
│   ├── data_acquisition_sentinel2.py
│   └── pre_process_merging_band_s2.py
│
├── output/
│   ├── sen_1/
│   └── sen_2/
│
└── reports/
    ├── final_report.pdf
    

```

## 🛰️ 1. Data Acquisition (Automated)

Automated downloading scripts:
- **Sentinel‑1 SAR:** `data_acquisition_sentinel1.py`
- **Sentinel‑2 Optical:** `data_acquisition_sentinel2.py`

These scripts:
✔ Query API  
✔ Filter by ROI  
✔ Filter by date range & cloud cover  
✔ Automatically download pre/post event datasets  

Credentials are *NOT* included.  

---

## 🛠️ 2. Pre‑processing & co-registration Workflow

### Sentinel‑2 Pre‑processing  
Performed using Python + QGIS:
- Band merging using: **`pre_process_merging_band_s2.py`**
- Cropping using QGIS → *GDAL Clip Raster by Extent*
- Resampling using QGIS → *Layer Properties → Resampling*

### Sentinel‑1 Pre‑processing  
Performed using SNAP + QGIS  
Detailed steps documented inside **reports/final_report.pdf**

Processed outputs stored inside:

```
data/Processed/sentinel_1/
data/Processed/sentinel_2/
```

---

## 🔍 3. Change Detection

### Sentinel‑1  
Script: `change_detection_S1.py`  
Uses:
- Image ratioing  
- Thresholding  
- Morphological filtering  

### Sentinel‑2  
Script: `change_detection_s2.py`  
Uses:
- PCA  
- Band differencing  
- NDVI‑based change evaluation  
- Morphological cleanup  

Outputs saved in:
```
output/sentinel_1/
output/sentinel_2/
```

---

## 📓 4. Included Notebooks

| Notebook | Purpose |
|---------|---------|
| `data_acquisition_sentinel1.ipynb` | SAR download workflow |
| `data_acquisition_sentinel2.ipynb` | Optical download workflow |
| `pre_process_merging_band_s2.ipynb` | S2 merging |
| `change_detection_S1.ipynb` | SAR change detection |
| `change_detection_s2.ipynb` | Optical change detection |

---

## 📦 5. Installation

Install all dependencies:
```
pip install -r requirements.txt
```

---

## ▶️ 6. Running the Pipeline

### Step 1 — Download Data
```
python src/data_acquisition_sentinel1.py
python src/data_acquisition_sentinel2.py
```

### Step 2 — Preprocess Images
```
python src/pre_process_merging_band_s2.py
```
(Sentinel‑1 preprocessing done externally in SNAP)

### Step 3 — Run Change Detection
```
python src/change_detection_S1.py
python src/change_detection_s2.py
```

### Step 4 — Review outputs
Check the `/output/` folder.

---

## 📑 7. Reporting  
The **final_report.pdf** includes:
- Data overview  
- Preprocessing steps  
- Change detection methodology  
- Visual outputs  
- Interpretation & accuracy assessment  
- Recommendations  

---

## ⭐ Summary  
This repository provides a complete automated and semi-automated EO–SAR workflow combining data acquisition, preprocessing, and change analysis across two major satellite sensors.


