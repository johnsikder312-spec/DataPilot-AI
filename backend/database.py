"""
database.py

Handles everything related to the SQLite database:
- creating the "students" table
- filling it with sample data (only the first time)
- describing the schema (used to tell the LLM what tables/columns exist)
- safely running a SELECT query and returning the results

Nothing here talks to the LLM or the web framework. Keeping it isolated
makes it easy to test or swap out later.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "students.db"

# Sample data used to seed the database on first run.
SAMPLE_STUDENTS = [
    ("Aarav Sharma", 20, "Computer Science", 88, "Kolkata"),
    ("Priya Das", 21, "Electronics", 76, "Mumbai"),
    ("Rohan Mehta", 19, "Computer Science", 92, "Delhi"),
    ("Sneha Roy", 22, "Mechanical", 65, "Kolkata"),
    ("Karan Verma", 20, "Civil", 58, "Pune"),
    ("Ananya Iyer", 21, "Computer Science", 81, "Chennai"),
    ("Vikram Singh", 23, "Electronics", 70, "Delhi"),
    ("Ishita Banerjee", 20, "Mechanical", 84, "Kolkata"),
    ("Arjun Nair", 22, "Civil", 45, "Bangalore"),
    ("Kavya Reddy", 19, "Computer Science", 95, "Hyderabad"),
    ("Rahul Gupta", 21, "Electronics", 60, "Mumbai"),
    ("Meera Pillai", 20, "Mechanical", 73, "Kochi"),
    ("Aditya Kumar", 22, "Computer Science", 55, "Patna"),
    ("Divya Menon", 21, "Civil", 89, "Kochi"),
    ("Siddharth Rao", 23, "Electronics", 67, "Chennai"),
    ("Neha Chatterjee", 20, "Computer Science", 79, "Kolkata"),
    ("Manish Joshi", 22, "Mechanical", 62, "Pune"),
    ("Pooja Agarwal", 19, "Civil", 91, "Delhi"),
    ("Vivek Malhotra", 21, "Electronics", 83, "Mumbai"),
    ("Shreya Ghosh", 20, "Computer Science", 87, "Kolkata"),
]

TABLE_NAME = "students"

# Single source of truth for the schema: (column name, SQL type for CREATE TABLE,
# plain-word type shown to the LLM). Both the table creation and the schema
# description sent to the LLM are built from this one list, so they can
# never drift apart.
COLUMNS = [
    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT", "integer"),
    ("name", "TEXT NOT NULL", "text"),
    ("age", "INTEGER NOT NULL", "integer"),
    ("department", "TEXT NOT NULL", "text"),
    ("marks", "INTEGER NOT NULL", "integer"),
    ("city", "TEXT NOT NULL", "text"),
]


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create the table and insert sample rows, but only if it's empty."""
    conn = get_connection()
    cur = conn.cursor()

    columns_sql = ",\n            ".join(f"{name} {sql_type}" for name, sql_type, _ in COLUMNS)
    cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (\n            {columns_sql}\n        )")

    cur.execute("SELECT COUNT(*) FROM students")
    count = cur.fetchone()[0]

    if count == 0:
        cur.executemany(
            "INSERT INTO students (name, age, department, marks, city) VALUES (?, ?, ?, ?, ?)",
            SAMPLE_STUDENTS,
        )
        conn.commit()

    conn.close()


def get_schema_text() -> str:
    """
    Builds a plain-text description of the schema from COLUMNS, sent to the
    LLM as context so it knows what tables/columns it can write SQL against.

    Produces:
        students:
        - id: integer
        - name: text
        ...
    """
    lines = [f"{TABLE_NAME}:"]
    lines += [f"- {name}: {type_label}" for name, _, type_label in COLUMNS]
    return "\n".join(lines)


def run_select_query(sql: str):
    """
    Executes a SELECT query and returns (columns, rows).
    Assumes the caller has already validated that this is a safe SELECT query.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [description[0] for description in cur.description] if cur.description else []
    conn.close()
    return columns, rows
