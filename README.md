# Immune X — Preventive Immune Memory Banking Engine

Immune X is an AI-driven preventive immune memory banking platform. It integrates patient cellular profiling, longevity risk assessment, and clinical biobanking indices to preserve high-quality immune cells (like T Memory Stem Cells - $T_{SCM}$) before age-associated immune decline (immunosenescence) occurs.

This repository contains the MVP implementation, featuring a highly modular, deterministic mathematical equation engine and a polished Streamlit user interface. The codebase is architected to allow seamless hot-swapping of mathematical equations with trained Machine Learning (ML) models in the future.

---

## 🚀 Key Features

* **Cascading Math Engine**: Automatically calculates **11 complex immunological metrics** from **23 raw inputs**.
* **Clinical Unit Normalization**: Supports direct input of raw laboratory units (e.g., CRP in mg/L, IL-6 in pg/mL, CD4/CD8 ratio) and automatically normalizes them to a 0-100 scale using clinical boundary helpers.
* **Premium Dashboard UI**: Built with Streamlit and styled with a custom Slate/Teal theme, featuring interactive Plotly gauges, radar charts, biological vs. chronological age comparisons, and live developer payload inspect tools.
* **Modularity**: Fully decoupled engine schema and predictions layer, making it compatible with future machine learning model deployments (e.g. XGBoost, Random Forest).
* **Unit Tests**: Full test coverage of equations and boundary validation using `pytest`.

---

## 📁 Repository Structure

```text
├── .streamlit/
│   └── config.toml          # Custom theme configuration for Streamlit
├── app/
│   ├── dashboard.py         # Output metrics, charts (gauges, radar, bar), and clinical rules
│   ├── style.css            # Custom CSS for dark-mode glassmorphic aesthetics
│   └── ui_components.py     # Multi-tab layout for the 23 raw inputs
├── assets/
│   └── immune_x_pipeline.png# Generated system architecture & pipeline graphic
├── docs/
│   └── report.md            # Extensive system design and mathematical documentation
├── src/
│   ├── engine/
│   │   ├── __init__.py      # Package entrypoint
│   │   ├── calculations.py  # Math equations calculation functions
│   │   └── schemas.py       # Pydantic validation models for inputs and outputs
│   ├── models/
│   │   └── placeholder.py   # Stub indicating how to swap equations with ML models
│   └── utils/
│       ├── __init__.py      # Package entrypoint
│       └── helpers.py       # Laboratory unit normalization functions
├── tests/
│   └── test_engine.py       # Unit tests verifying equation outputs and validation
├── main.py                  # Streamlit application main entry point
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

---

## 🛠️ Setup & Installation

### Prerequisites
* Python 3.9 or higher

### 1. Clone the repository and navigate to the root
```bash
cd Immune_X
```

### 2. Create and activate a virtual environment
**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Unit Tests
To verify that the engine calculations are working correctly and match all mathematical specifications:
```bash
pytest
```

### 5. Launch the Streamlit App
```bash
streamlit run main.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## ⚙️ Mathematical Engine Inputs

The calculation engine consumes 23 input variables grouped into four categories:
1. **Biomarkers & Lab Results (7)**: `CRP`, `IL6`, `TNFa`, `TSCM`, `TCRD`, `CD4_CD8_Ratio`, `NaiveT`.
2. **Demographics & Lifestyle (7)**: `Age`, `Expected_Lifespan`, `BMI_Score`, `Smoking_Score`, `Exercise_Score`, `Sleep_Score`, `Comorbidity_Score`.
3. **Medical History (6)**: `Antibody_Response`, `T_cell_Response`, `Response_Durability`, `Metabolic_Score`, `Cardiovascular_Score`, `Immune_Health_Base_Score`.
4. **AI / Historical Data (3)**: `ImmuneAge`, `DeltaImmuneAge`, `DeltaIMQS`.
