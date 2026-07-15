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

### Phase 3: Logical Corrections & Input Automation [Latest]
- **Re-banking Logic Refinement (Risk/Decline Index)**:
  - Re-Banking Index formula uses the official engine specifications: `ReBankingIndex = 0.50(DeltaImmuneAge) - 0.30(DeltaIMQS) + 0.20(IDRS)`.
  - The index is a **Risk/Decline Index**. 
  - **High Score (>= 5.0)**: Represents immune decline. The automated decision is **Keep** (retain the previous excellent sample).
  - **Low Score (< 5.0)**: Represents optimal health improvement. The automated decision is **Rebank** (capture the superior state immediately).
  - **First Session**: The system explicitly skips calculating this index and displays **N/A - No Previously Banked Cells**.
- **Temporal Input Automation**:
  - Removed manual editing of `DeltaImmuneAge` and `DeltaIMQS` from the input form.
  - **First Session**: Both Delta fields are automatically set to `0.0` (forced and read-only).
  - **Subsequent Sessions**:
    - System automatically fetches the previous session's `ImmuneAge` and `IMQS` from the database.
    - Live-calculates and displays `DeltaImmuneAge = Current_ImmuneAge - Previous_ImmuneAge`.
    - Live-calculates and displays `DeltaIMQS = Current_IMQS - Previous_IMQS` dynamically inside the Streamlit tabs.
    - Fields are locked (disabled) to prevent doctor entry errors.

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
             └── No  ──► Load last session from DB
                         Auto-calculate Deltas dynamically in UI
                         │
                         ▼
             [Doctor Submits Form]
                         │
                         ▼
         [calculate_immune_metrics(inputs)]
                         │
                         ▼
        [Is Current Health Better than Last?]
        ├── Yes (RBI < 5.0)  ──► Suggest Re-banking (Rebank)
        └── No  (RBI >= 5.0) ──► Keep Existing Sample (Keep)
                         │
                         ▼
         [Save Session outputs to DB & Rerun]
```
