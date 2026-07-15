# Immune X — Preventive Immune Memory Banking Engine

**Idea Owner: Ahmed Allam**

Immune X is an AI-driven preventive immune memory banking platform for licensed medical professionals and laboratory specialists. It integrates patient cellular profiling, longevity risk assessment, and clinical biobanking indices to preserve high-quality immune cells (like T Memory Stem Cells — $T_{SCM}$) before age-associated immune decline (immunosenescence) occurs.

---

## 🚀 Key Features

* **Patient Management**: Register patients by National ID and maintain a persistent clinical record accessible by any authorised clinician.
* **Multi-Session Testing**: Each patient can have unlimited immune assessment sessions. Results are stored permanently in a cloud MySQL database.
* **Cascading Math Engine**: Automatically calculates **11 complex immunological metrics** from **23 raw inputs** per session.
* **Clinical Unit Normalization**: Supports direct input of raw laboratory units (e.g., CRP in mg/L, IL-6 in pg/mL, CD4/CD8 ratio) and automatically normalises them to a 0–100 scale.
* **Session Comparison & Best-Session Detection**: When a patient has more than one session, a trend chart (IHI + BES over time) is displayed, and the best session (highest IHI) is highlighted with a ⭐ star.
* **Quality Badges**: Each session is labelled 🟢 Optimal / 🟡 Fair / 🔴 High Risk based on IHI and BES thresholds.
* **Premium Medical Dashboard UI**: Dark-mode glassmorphic Streamlit UI with interactive Plotly gauges, radar charts, biological vs. chronological age comparisons, and a full 23-input summary per session.
* **Modularity**: Fully decoupled engine, schema, and database layers — ready for ML model hot-swap in the future.
* **Unit Tests**: Full test coverage of equations and boundary validation using `pytest`.

---

## 📁 Repository Structure

```text
├── .streamlit/
│   ├── config.toml          # Custom theme configuration for Streamlit
│   └── secrets.toml         # [LOCAL ONLY — NOT committed] Database credentials
├── app/
│   ├── pages/
│   │   ├── page_home.py     # Home page: register/open patient by National ID
│   │   ├── page_patient.py  # Patient profile: session list, comparison, add session
│   │   └── page_session_result.py  # Full dashboard + 23-input summary for one session
│   ├── dashboard.py         # Output metrics, charts (gauges, radar, bar), clinical rules
│   ├── style.css            # Custom CSS: dark-mode glassmorphic + clinical components
│   └── ui_components.py     # Header + multi-tab 23-input form
├── assets/
│   └── immune_x_pipeline.png  # System architecture & pipeline graphic
├── docs/
│   └── report.md            # System design, math, DB schema, workflow documentation
├── src/
│   ├── database/
│   │   ├── __init__.py      # Package entrypoint
│   │   └── db.py            # MySQL connection pool, init_db, patient/session CRUD
│   ├── engine/
│   │   ├── __init__.py      # Package entrypoint
│   │   ├── calculations.py  # Math equations calculation functions
│   │   └── schemas.py       # Pydantic validation models for inputs and outputs
│   ├── models/
│   │   └── placeholder.py   # Stub for future ML model swap
│   └── utils/
│       ├── __init__.py      # Package entrypoint
│       └── helpers.py       # Laboratory unit normalization functions
├── tests/
│   └── test_engine.py       # Unit tests verifying equation outputs and validation
├── main.py                  # Streamlit application entry point (page router)
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

---

## 🛠️ Setup & Installation

### Prerequisites
* Python 3.9 or higher
* A MySQL database (e.g., freesqldatabase.com account)

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

### 4. Configure Database Secrets

Create the file `.streamlit/secrets.toml` (this file must **NOT** be committed to git):

```toml
[mysql]
host = "sql12.freesqldatabase.com"
database = "your_database_name"
user = "your_database_user"
password = "your_database_password"
port = 3306
```

> ⚠️ **Never hard-code credentials in source files.** The app reads them exclusively from `st.secrets["mysql"]`.

For **Streamlit Cloud** deployments, paste the same block into your app's **Secrets** section in the Streamlit Cloud dashboard.

### 5. Run the Unit Tests
```bash
python -m pytest
```

### 6. Launch the Streamlit App
```bash
streamlit run main.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🏥 Clinical Workflow

The portal is structured as a 3-page flow navigated via `st.session_state`:

```
Home Page  →  Patient Profile  →  Session Results
```

### Page 1 — Home
* **Register New Patient**: Enter National ID → "Register Patient". The system creates a new DB record.
* **Open Patient Profile**: Enter National ID → "Open Profile". Navigates to the patient's record.
* Duplicate National IDs are rejected with a clear error message.

### Page 2 — Patient Profile
* Displays patient header (National ID + registration date).
* **Session History**: A list of all past sessions with:
  * Session number, date, IHI score, BES score
  * Quality badge: 🟢 Optimal (IHI ≥ 75) / 🟡 Fair (IHI ≥ 50) / 🔴 High Risk (IHI < 50)
  * ⭐ Star marking the best session (highest IHI) when > 1 session exists
* **Session Trend Chart**: IHI and BES plotted over time with the best session highlighted.
* **Add New Session**: Expandable form with the full 23-input assessment. Saves to DB on submit.

### Page 3 — Session Results
* Shows the full visual dashboard (gauges, radar chart, age comparison, metric cards, clinical recommendations) for the selected session.
* **Input Summary**: Expandable panel listing all 23 recorded values, grouped by category.
* Navigate back to the patient profile at any time.

---

## 📊 Session Quality Classification

| IHI Score | Badge | Interpretation |
|---|---|---|
| 75 – 100 | 🟢 Optimal | Excellent immune health — ideal for biobanking |
| 50 – 74 | 🟡 Fair | Acceptable — lifestyle improvements recommended |
| 0 – 49 | 🔴 High Risk | Elevated senescence risk — pre-treatment advised |

| BES Score | Badge | Interpretation |
|---|---|---|
| 75 – 100 | ✅ Highly Eligible | Immediate biobanking recommended |
| 50 – 74 | 🔵 Eligible | Eligible with minor optimisation needed |
| 0 – 49 | ⚠️ Not Eligible | Postpone — address inflammation/health metrics |

### 🎯 Longitudinal Comparison — IDI & Upgrade Potential

The platform features two longitudinal comparison indicators comparing the current test session against the patient's best stored biobank sample:

* **Immune Decline Index (IDI)**: Measures cellular deterioration since banking. IDI values are classified as:
  * **0 – 20**: Minimal Decline
  * **21 – 40**: Mild Decline
  * **41 – 60**: Moderate Decline
  * **61 – 80**: Significant Decline
  * **81 – 100**: Severe Decline
* **Upgrade Potential Score (UPS)**: Determines whether the current profile is biologically superior to the stored sample.
  * **UPS > 0**: Potential Sample Upgrade Detected (recommends saving new peak immunity sample).
  * **UPS <= 0**: Retain Original Banked Sample (original stored sample is superior).

---

## 🗄️ Database Schema

The app auto-creates the following tables on first launch:

```sql
CREATE TABLE IF NOT EXISTS patients (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    national_id  VARCHAR(100) UNIQUE NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    patient_national_id  VARCHAR(100) NOT NULL,
    session_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inputs_json          TEXT NOT NULL,
    outputs_json         TEXT NOT NULL,
    ihi_score            FLOAT NOT NULL,
    bes_score            FLOAT NOT NULL,
    FOREIGN KEY (patient_national_id)
        REFERENCES patients(national_id)
        ON DELETE CASCADE
);
```

---

## ⚙️ Mathematical Engine Inputs

The calculation engine consumes 23 input variables grouped into four categories:
1. **Biomarkers & Lab Results (7)**: `CRP`, `IL6`, `TNFa`, `TSCM`, `TCRD`, `CD4_CD8_Ratio`, `NaiveT`.
2. **Demographics & Lifestyle (7)**: `Age`, `Expected_Lifespan`, `BMI_Score`, `Smoking_Score`, `Exercise_Score`, `Sleep_Score`, `Comorbidity_Score`.
3. **Medical History (6)**: `Antibody_Response`, `T_cell_Response`, `Response_Durability`, `Metabolic_Score`, `Cardiovascular_Score`, `Immune_Health_Base_Score`.
4. **AI / Historical Data (4)**: `ImmuneAge`, `DeltaImmuneAge`, `DeltaIMQS`, `TimeSinceBankingFactor`.
