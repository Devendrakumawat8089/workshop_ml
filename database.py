from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "clinic.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                specialization TEXT NOT NULL,
                timing TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                blood_group TEXT NOT NULL
            )
        """)

        doctor_count = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        if doctor_count == 0:
            conn.executemany(
                "INSERT INTO doctors (name, specialization, timing) VALUES (?, ?, ?)",
                [
                    ("Dr. Sharma", "General Physician", "10 AM - 2 PM"),
                    ("Dr. Mehta", "Cardiologist", "4 PM - 8 PM"),
                ],
            )

        patient_count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if patient_count == 0:
            conn.executemany(
                "INSERT INTO patients (name, age, city, blood_group) VALUES (?, ?, ?, ?)",
                [
                    ("Rahul Sharma", 32, "Jaipur", "B+"),
                    ("Priya Verma", 28, "Jaipur", "O+"),
                    ("Amit Singh", 45, "Ajmer", "A+"),
                ],
            )


def get_doctor(name: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, specialization, timing FROM doctors WHERE LOWER(name) = LOWER(?)",
            (name.strip(),),
        ).fetchone()
        return dict(row) if row else None


def get_patient(patient_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, age, city, blood_group FROM patients WHERE id = ?",
            (patient_id,),
        ).fetchone()
        return dict(row) if row else None
