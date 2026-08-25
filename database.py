
import sqlite3
import pandas as pd

DB_NAME = "expenses.db"

CATEGORIES = ["Food", "Travel", "Utilities", "Entertainment", "Health", "Shopping", "Other"]


def get_connection():
    """Create and return a new database connection."""
    return sqlite3.connect(DB_NAME)


def init_db():
 
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_expense(date, category, amount, description):
    """Insert a new expense record."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        (date, category, amount, description),
    )
    conn.commit()
    conn.close()


def get_all_expenses():
    """Return all expenses as a pandas DataFrame, sorted by most recent date first."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def delete_expense(expense_id):
    """Delete a single expense record by its id."""
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def clear_all_expenses():
    """Delete all expense records (used by the reset option)."""
    conn = get_connection()
    conn.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()
