import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASES_DIR = os.path.join(BASE_DIR, "databases")
os.makedirs(DATABASES_DIR, exist_ok=True)
DATABASE_FILE = os.path.join(DATABASES_DIR,"data.db")
EXPENSE_FILE = os.path.join(DATABASES_DIR,"Expenses.db")
FIXED_DATA = os.path.join(DATABASES_DIR, "perm_rec.json")

def create_table(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{username}" (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                fixed_income REAL DEFAULT 0,
                extra_income REAL DEFAULT 0,
                savings REAL DEFAULT 0,
                total_income REAL DEFAULT 0
            )
        """)
        conn.commit()

def connect_db(file=DATABASE_FILE):
    return sqlite3.connect(file)

def load_json(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump({}, f, indent=4)

    with open(filepath, 'r') as f:
        return json.load(f)
    
def save_json(filepath,data):
        with open(filepath, 'w') as f:
            json.dump(data,f, indent=4)
            return True