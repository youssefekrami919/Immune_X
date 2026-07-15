# IMMUNE X — System Walkthrough & Feature Log

**Idea Owner: Ahmed Allam**

This document tracks all features, architectural changes, logic updates, and database integrations implemented since the inception of the **Immune X** project.

---

## 🛠️ Complete Feature History & Pipeline

### Phase 1: Engine Foundation & Single-Page Calculator
- **Mathematical Engine**: Built a decoupled, cascading mathematical calculation engine to compute **11 immunological outputs** from **23 raw inputs** (`src/engine/`).
- **Pydantic Validation Schema**: Configured strict data typing and boundaries (`src/engine/schemas.py`).
- **Clinical Unit Normalization**: Standardised inputs (like CRP in mg/L and IL-6 in pg/mL) to a 0–100 scale using clinical boundary helpers (`src/utils/helpers.py`).
- **Initial Streamlit UI**: Created a dark-mode dashboard displaying gauge charts, a radar plot, biological vs. chronological age, and raw JSON payload inspect widgets.
- **Unit Tests**: Full test suite built via `pytest` to guarantee mathematical consistency.

### Phase 2: Clinical Overhaul & MySQL Database Integration
- **Multi-Page Layout**: Re-architected `main.py` into a 3-page state-based portal (`home`, `patient`, `session_result`).
- **Database Persistence**: Set up a MySQL database layer (`src/database/db.py`) storing patient records and testing session JSON structures.
- **Longitudinal Trend Charting**: Enabled IHI and BES comparison plotting across all sessions chronologically.
- **Re-Banking Index Gauge**: Added a visual index gauge with Keep/Rebank zones to show if cell updates are needed.

### Phase 3: Logical Corrections & Custom Longitudinal Engine [Latest]
- **Removal of Re-Banking Index (RBI)**:
  - Completely removed the conceptually incorrect RBI recommendation engine. Immune decline must not trigger re-banking a biologically inferior current sample.
- **Introduction of Immune Decline Index (IDI)**:
  - Measures immune deterioration relative to the patient's best stored sample.
  - Formula: `IDI = 0.50(DeltaImmuneAgeScore) + 0.30(DeltaIMQS) + 0.20(TimeSinceBankingFactor)`.
  - Classifies decline into stepwise ranges (Minimal, Mild, Moderate, Significant, Severe).
- **Introduction of Upgrade Potential Score (UPS)**:
  - Determines whether the current profile is biologically superior to the stored sample.
  - Formula: `UPS = 0.40(CurrentIMQS - BankedIMQS) + 0.30(CurrentTSCM - BankedTSCM) + 0.30(CurrentIRS - BankedIRS)`.
  - UPS > 0 triggers a "Sample Upgrade Suggested" decision; UPS <= 0 recommends retaining the original stored sample.
- **Immune Resiliency Score (IRS)**:
  - Added new output capacity measure: `IRS = 0.40(TSCM) + 0.30(VRS) + 0.30(Lifestyle)`.
- **Temporal Input Automation**:
  - Automatically fetches the patient's best historical session from the DB to act as the reference banked sample.
  - Live-calculates and displays `DeltaImmuneAge` and `DeltaIMQS` on the UI.
  - Added `TimeSinceBankingFactor` to form inputs.

---

## 🗄️ Database SQL Schema

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

## 🧭 Application Data Flow

```text
       [Doctor registers/selects National ID]
                         │
                         ▼
             [Is it the first session?]
             ├── Yes ──► Delta fields = 0.0 (disabled)
             └── No  ──► Load best session from DB as Banked Profile
                         Auto-calculate Deltas dynamically in UI
                         │
                         ▼
             [Doctor Submits Form]
                         │
                         ▼
         [calculate_immune_metrics(inputs, banked_metrics)]
                         │
                         ▼
             [Is Current Sample Better?]
             ├── Yes (UPS > 0)  ──► Suggest Sample Upgrade (Upgrade)
             └── No  (UPS <= 0) ──► Retain Stored Sample (Keep)
                         │
                         ▼
          [Save Session outputs to DB & Rerun]
```
