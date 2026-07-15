# Immune X — Technical & Mathematical Engine Report

This report provides a detailed technical specification of the Immune X MVP calculation engine, including the mathematical formulas, pipeline architecture, and cascading scoring dependencies.

---

## 🖼️ System Pipeline Overview

Below is the design concept representing the cell profiling, mathematical cascading, and immune bank eligibility pipeline of the Immune X platform:

![Immune X System Concept](../assets/immune_x_pipeline.png)

---

## 🛠️ Pipeline Architecture & Data Flow

The platform separates validation, mathematical calculation, and user presentation. The engine uses **Pydantic** to enforce data integrity and standard validation rules (e.g. bounding input values strictly between 0 and 100).

The overall process flows as follows:
1. **Input Stage**: The user supplies 23 raw parameters in the UI (grouped by Biomarkers, Demographics/Lifestyle, Medical History, and Temporal/Historical Data).
2. **Clinical Normalization**: Raw values (like CRP in mg/L or CD4/CD8 ratio) are scaled to a standard 0-100 score using clinical reference curves in `src/utils/helpers.py`.
3. **Pydantic Validation**: Parameters are parsed into the `ImmuneInputs` schema class.
4. **Intermediate Equation Phase**: Calculations 1 through 6 are performed sequentially, deriving supporting metrics.
5. **Core Equation Phase**: Core scores (IMQS, BES, IDRS, ReBankingIndex, and IHI) are calculated by drawing from both the raw inputs and the freshly calculated intermediate scores.
6. **Output Presentation**: Outputs are parsed into the `ImmuneOutputs` model and displayed on the interactive Streamlit dashboard.

---

## 🧮 Detailed Mathematical Formulas

### A. Supporting Equations (Stage 1)

These 5 equations calculate intermediate profiles used in subsequent core scores.

#### 1. Inflammation Score (IS)
Combines three prominent pro-inflammatory biomarkers (CRP, IL-6, and TNF-alpha) to measure systemic inflammation.
$$IS = 0.40(CRP) + 0.30(IL6) + 0.30(TNFa)$$

#### 2. Lifestyle Score (LS)
Synthesizes physical habits (exercise, sleep, body composition, and smoking).
$$LS = 0.30(Exercise\_Score) + 0.30(Sleep\_Score) + 0.20(BMI\_Score) + 0.20(Smoking\_Score)$$

#### 3. Vaccine Response Score (VRS)
Estimates adaptive immune reactivity based on peak titers and antibody half-life.
$$VRS = 0.50(Antibody\_Response) + 0.30(T\_cell\_Response) + 0.20(Response\_Durability)$$

#### 4. Health Score (HS)
Establishes the patient's general physiological base fitness.
$$HS = 0.35(Metabolic\_Score) + 0.35(Cardiovascular\_Score) + 0.30(Immune\_Health\_Base\_Score)$$

#### 5. Age Factor (AF)
Calculates a relative aging index representing expected lifespan remaining.
$$AF = 100 - \left(\frac{Age}{Expected\_Lifespan} \cdot 100\right)$$

---

### B. Core Equations (Stage 2)

These equations produce the primary clinical indicators shown in the dashboard.

#### 6. Immune Age Gap
Represents biological immune age acceleration. Negative values denote a younger, healthier immune profile.
$$ImmuneAgeGap = ImmuneAge - Age$$

#### 7. Immune Memory Quality Score (IMQS)
Evaluates the quantity and quality of antigen-experienced cells. It relies on T Memory Stem Cells ($T_{SCM}$), T-cell Receptor Diversity ($TCRD$), Naive T cells, and intermediate indicators ($VRS, IS, LS, AF$).
$$IMQS = 0.25(TSCM) + 0.20(TCRD) + 0.15(CD4\_CD8\_Ratio) + 0.10(NaiveT) + 0.10(VRS) + 0.10(IS) + 0.05(LS) + 0.05(AF)$$

#### 8. Biobanking Eligibility Score (BES)
Determines if a patient's immune cells are high quality enough to bank. The $AgeFactor$ (AF) represents the $AgeScore$ in this calculation.
$$BES = 0.60(IMQS) + 0.20(HS) + 0.20(AgeFactor)$$

#### 9. Immune Decline Risk Score (IDRS)
Estimates the rate of immunosenescence.
$$IDRS = 0.30(IS) + 0.25(ImmuneAgeGap) + 0.15(BMI\_Score) + 0.15(Smoking\_Score) + 0.15(Comorbidity\_Score)$$

#### 10. Re-Banking Index (RBI)
Used to flag if previous biobanked samples need updating or cell boosting.
$$ReBankingIndex = 0.50(DeltaImmuneAge) + 0.30(DeltaIMQS) + 0.20(IDRS)$$

#### 11. Immune Health Index (IHI)
The high-level overall summary metric of immune system durability.
$$IHI = 0.40(IMQS) + 0.30(100 - IDRS) + 0.30(BES)$$

---

## 🔗 Cascading Dependency Map

The engine is highly optimized; instead of asking the user to manually calculate and input scores, the calculation engine forms a directed acyclic dependency graph (DAG) where outputs cascade:

```text
               ┌── [ CRP, IL6, TNFa ] ──────────────────> Inflammation Score (IS) ──┐
               ├── [ Exercise, Sleep, BMI, Smoking ] ────> Lifestyle Score (LS) ────┤
               ├── [ Antibody, T_cell, Durability ] ────> Vaccine Score (VRS) ─────┤
               ├── [ Age, Expected_Lifespan ] ──────────> Age Factor (AF) ─────────┼──> IMQS ──┐
               │                                                                   │           │
[ Raw Inputs ] ├── [ TSCM, TCRD, CD4_CD8_Ratio, NaiveT ] ──────────────────────────┘           │
               ├── [ Metabolic, Cardiovascular, Base ] ──> Health Score (HS) ──────────┐       ├──> BES ──┐
               │                                                                       │       │          │
               ├── [ ImmuneAge, Age ] ──────────────────> Immune Age Gap ──┐           ├──> ───┼──> ──────┼──> IHI
               │                                                           ├──> IDRS ──┤       │          │
               ├── [ Comorbidity ] ────────────────────────────────────────┘     │     │       │          │
               │                                                                 ▼     │       │          │
               └── [ DeltaImmuneAge, DeltaIMQS ] ────────────────────────> ReBankingIndex ┘       ┘          ┘
```

---

## 🎯 Implementation details

All calculations are encapsulated inside the package function:
* `src.engine.calculations.calculate_immune_metrics`

Input structures are checked against strict Pydantic requirements:
* `src.engine.schemas.ImmuneInputs`

This design ensures that if any mathematical equation is replaced in the future with a machine learning model, only the model execution logic inside `src.models/` needs to change; the validation boundary, API structure, and frontend Streamlit app will remain completely untouched.

---

## 🏥 Clinical Platform Architecture (v2)

**Idea Owner: Ahmed Allam**

Version 2 of IMMUNE X transforms the single-page calculation tool into a full multi-patient clinical management platform designed for use by licensed medical professionals and laboratory specialists.

### Application Pages

The app now uses a **3-page navigation model** managed via `st.session_state["page"]`:

| Page | Key | Description |
|---|---|---|
| Home | `home` | Register new patient or open existing patient by National ID |
| Patient Profile | `patient` | View session history, compare sessions, add new session |
| Session Results | `session_result` | Full dashboard + 23-input summary for one selected session |

### Data Flow

```text
Doctor enters National ID
         │
         ▼
  ┌─────────────────┐
  │  Home Page      │ ── Register ──► MySQL: INSERT patients
  │  (page_home)    │ ── Open ──────► MySQL: SELECT patients WHERE national_id = ?
  └─────────────────┘
         │
         ▼ (on patient found)
  ┌─────────────────────────┐
  │  Patient Profile        │ ── Load sessions ──► MySQL: SELECT sessions WHERE national_id = ?
  │  (page_patient)         │ ── Save session ───► calculate_immune_metrics() ──► MySQL: INSERT sessions
  └─────────────────────────┘
         │
         ▼ (on "Show Results")
  ┌─────────────────────────┐
  │  Session Results        │ ── Reconstructs ImmuneInputs + ImmuneOutputs from JSON
  │  (page_session_result)  │ ── Calls render_dashboard() with stored data
  └─────────────────────────┘
```

---

## 🗄️ Database Schema

The application uses a remote MySQL database (freesqldatabase.com). Tables are automatically created on first launch via `init_db()`.

### `patients` table

| Column | Type | Description |
|---|---|---|
| `id` | INT AUTO_INCREMENT PK | Internal identifier |
| `national_id` | VARCHAR(100) UNIQUE | Patient National ID (primary lookup key) |
| `created_at` | TIMESTAMP | Registration timestamp |

### `sessions` table

| Column | Type | Description |
|---|---|---|
| `id` | INT AUTO_INCREMENT PK | Internal session identifier |
| `patient_national_id` | VARCHAR(100) FK | References `patients.national_id` |
| `session_date` | TIMESTAMP | Session creation timestamp |
| `inputs_json` | TEXT | All 23 `ImmuneInputs` fields serialised as JSON |
| `outputs_json` | TEXT | All 11 `ImmuneOutputs` fields serialised as JSON |
| `ihi_score` | FLOAT | Denormalised IHI for fast sorting/comparison |
| `bes_score` | FLOAT | Denormalised BES for fast filtering |

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

## 📊 Session Quality Classification

Sessions are automatically classified and badged based on IHI and BES scores:

### Immune Health Index (IHI) — Overall Immune State

| Range | Badge | Clinical Interpretation |
|---|---|---|
| IHI ≥ 75 | 🟢 Optimal | Excellent immune state; cells are highly suitable for banking |
| 50 ≤ IHI < 75 | 🟡 Fair | Acceptable; lifestyle optimisation recommended before banking |
| IHI < 50 | 🔴 High Risk | Elevated immunosenescence; pre-treatment stabilisation required |

### Biobanking Eligibility Score (BES)

| Range | Badge | Clinical Interpretation |
|---|---|---|
| BES ≥ 75 | ✅ Highly Eligible | Immediate biobanking recommended |
| 50 ≤ BES < 75 | 🔵 Eligible | Eligible with minor inflammatory marker improvement |
| BES < 50 | ⚠️ Not Eligible | Postpone banking; address comorbidities and inflammation first |

### Best Session Detection

When a patient has more than one session, the system identifies the **best session** as the one with the highest IHI score. This session is:
- Marked with a ⭐ star in the session list card
- Highlighted with a gold `#FFBE0B` star marker on the trend chart

The session trend chart plots both IHI and BES across all sessions chronologically, with:
- Reference lines at IHI = 75 (Optimal threshold) and IHI = 50 (Fair threshold)
- A secondary BES dotted line for cross-metric trend analysis

### Re-Banking Index — Visual Risk Gauge

The Re-Banking Index uses a dedicated horizontal gauge to map the raw clinical calculation to a unified 0-100 visual scale. This allows clinicians to instantly interpret the urgency of taking new cell samples:

#### Visual Mapping Scale & Logic
- **Raw Clinical Range**: Maps the values from **`-10.0`** to **`20.0`** onto a **`0`** to **`100`** bar position.
- **Formula**: `BarPosition = ((RawValue - (-10.0)) / 30.0) * 100.0` (clamped between 0 and 100).
- **Rebank Threshold**: The clinical re-banking threshold of **`5.0`** corresponds exactly to position **`50`** on the bar.
- **Peak Health Capture Logic**: Re-banking is suggested (`RBI >= 5.0`) **only** when the current session's health is **better** than the previous session's health (meaning biological immune age got younger and/or memory quality improved). If there is no change or a decline in health, the system recommends **Keeping** the old sample (`RBI < 5.0`) since the old sample is of superior quality.

#### Visual Zones
- ✅ **Keep Zone (Bar position 0 to 50)**: Raw value is below 5.0. Indicates stable, declining, or first-session status; current biobanked samples are sufficient.
- 🔄 **Rebank Zone (Bar position 50 to 100)**: Raw value is at or above 5.0. Indicates significant improvement in immune health since the last storage; immediate re-banking is recommended to preserve this peak state.

#### Temporal Input Automation
- **First Session**: Both `DeltaImmuneAge` and `DeltaIMQS` are automatically set to `0.0` (forced/read-only).
- **Subsequent Sessions**: System dynamically retrieves the previous session's inputs/outputs from the database and live-calculates:
  - `DeltaImmuneAge = Current_ImmuneAge - Previous_ImmuneAge`
  - `DeltaIMQS = Current_IMQS - Previous_IMQS`
  These fields are disabled (read-only) in the user interface to guarantee data accuracy.

---

## 🔐 Secrets & Credentials

All database credentials are stored exclusively in `.streamlit/secrets.toml` (local) or Streamlit Cloud secrets (deployment). They are never present in source code.

The database layer (`src/database/db.py`) reads credentials via:
```python
cfg = st.secrets["mysql"]
```

Required keys: `host`, `database`, `user`, `password`, `port`.
