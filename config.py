import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASES_DIR = os.path.join(BASE_DIR, "databases")
os.makedirs(DATABASES_DIR, exist_ok=True)
DATABASE_FILE = os.path.join(DATABASES_DIR,"data.db")
FIXED_DATA = os.path.join(BASE_DIR, "perm_rec.json")

def create_table(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{username}" (
                timestamp DATETIME ,
                fixed_income REAL DEFAULT 0,
                extra_income REAL DEFAULT 0,
                expense REAL DEFAULT 0,
                savings REAL DEFAULT 0,
                total_expenses REAL DEFAULT 0,
                total_income REAL DEFAULT 0
            )
        """)
        conn.commit()

def connect_db():
    return sqlite3.connect(DATABASE_FILE)

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
    
def save_json(filepath,data):
        with open(filepath, 'w') as f:
            json.dump(data,f, indent=4)

def update(name):
     with connect_db() as conn:
          cursor = conn.cursor()

          cursor.execute(f"""SELECT sum(fixed_income) + sum(extra_income) From "{name}" """)
          total_income = cursor.fetchone()[0]

          cursor.execute(f"""UPDATE "{name}" SET total_income = ?""", (total_income,))
          conn.commit()

          return total_income