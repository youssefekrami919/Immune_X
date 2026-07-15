"""
Database layer for IMMUNE X.

All credentials are read from Streamlit secrets (st.secrets["mysql"]).
Never hard-code credentials in this file.

Expected secrets.toml structure:
    [mysql]
    host = "..."
    database = "..."
    user = "..."
    password = "..."
    port = 3306
"""

import json
import streamlit as st
import mysql.connector
from mysql.connector import pooling, Error


# ─────────────────────────────────────────────
# Connection Pool (cached for the app lifetime)
# ─────────────────────────────────────────────

@st.cache_resource
def _get_pool():
    """Create and cache a MySQL connection pool for the entire app session."""
    cfg = st.secrets["mysql"]
    pool = pooling.MySQLConnectionPool(
        pool_name="immunex_pool",
        pool_size=3,
        host=cfg["host"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        port=int(cfg["port"]),
        autocommit=True,
        connection_timeout=10,
    )
    return pool


def _get_conn():
    """Get a connection from the pool."""
    return _get_pool().get_connection()


# ─────────────────────────────────────────────
# Schema Initialization
# ─────────────────────────────────────────────

def init_db():
    """
    Create the `patients` and `sessions` tables if they do not exist.
    Called once on application startup.
    """
    create_patients = """
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            national_id VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    create_sessions = """
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_national_id VARCHAR(100) NOT NULL,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            inputs_json TEXT NOT NULL,
            outputs_json TEXT NOT NULL,
            ihi_score FLOAT NOT NULL,
            bes_score FLOAT NOT NULL,
            FOREIGN KEY (patient_national_id)
                REFERENCES patients(national_id)
                ON DELETE CASCADE
        )
    """
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(create_patients)
        cursor.execute(create_sessions)
        cursor.close()
        conn.close()
    except Error as e:
        st.error(f"Database initialization error: {e}")
        raise


# ─────────────────────────────────────────────
# Patient Operations
# ─────────────────────────────────────────────

def add_patient(national_id: str) -> dict:
    """
    Insert a new patient record.

    Returns:
        dict with keys 'success' (bool) and 'message' (str).
    """
    national_id = national_id.strip()
    if not national_id:
        return {"success": False, "message": "National ID cannot be empty."}

    sql = "INSERT INTO patients (national_id) VALUES (%s)"
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, (national_id,))
        cursor.close()
        conn.close()
        return {"success": True, "message": f"Patient '{national_id}' registered successfully."}
    except Error as e:
        if e.errno == 1062:  # Duplicate entry
            return {"success": False, "message": f"A patient with National ID '{national_id}' already exists."}
        return {"success": False, "message": f"Database error: {e}"}


def get_patient(national_id: str) -> dict | None:
    """
    Fetch a patient record by National ID.

    Returns:
        dict with keys 'id', 'national_id', 'created_at', or None if not found.
    """
    national_id = national_id.strip()
    sql = "SELECT id, national_id, created_at FROM patients WHERE national_id = %s"
    try:
        conn = _get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (national_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    except Error as e:
        st.error(f"Database error: {e}")
        return None


# ─────────────────────────────────────────────
# Session Operations
# ─────────────────────────────────────────────

def add_session(national_id: str, inputs_dict: dict, outputs_dict: dict) -> dict:
    """
    Insert a new test session for a patient.

    Args:
        national_id: Patient National ID (must already exist in patients table).
        inputs_dict: dict of all 23 ImmuneInputs fields.
        outputs_dict: dict of all 11 ImmuneOutputs fields.

    Returns:
        dict with keys 'success' (bool) and 'message' (str).
    """
    sql = """
        INSERT INTO sessions
            (patient_national_id, inputs_json, outputs_json, ihi_score, bes_score)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, (
            national_id.strip(),
            json.dumps(inputs_dict),
            json.dumps(outputs_dict),
            float(outputs_dict.get("IHI", 0.0)),
            float(outputs_dict.get("BES", 0.0)),
        ))
        cursor.close()
        conn.close()
        return {"success": True, "message": "Session saved successfully."}
    except Error as e:
        return {"success": False, "message": f"Database error: {e}"}


def get_sessions(national_id: str) -> list[dict]:
    """
    Fetch all sessions for a patient, ordered oldest-first.

    Returns:
        List of dicts with keys:
            'id', 'session_date', 'inputs_json', 'outputs_json',
            'ihi_score', 'bes_score'
    """
    sql = """
        SELECT id, session_date, inputs_json, outputs_json, ihi_score, bes_score
        FROM sessions
        WHERE patient_national_id = %s
        ORDER BY session_date ASC
    """
    try:
        conn = _get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (national_id.strip(),))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        st.error(f"Database error: {e}")
        return []
