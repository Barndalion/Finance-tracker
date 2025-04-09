from config import *
import json
import datetime

def get_balance(name):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT total_income FROM {name}""")
        total_income =  cursor.fetchone()

    with connect_db(EXPENSE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT total_expenses FROM "{name}" """)
        total_expenses = cursor.fetchone()

    if total_income is None:
        total_income = "0"
    if total_expenses is None:
        total_expenses = "0"

    savings = get_savings(name)

    balance = int(total_income[0]) - (int(total_expenses[0]) + int(savings))
    return balance

def get_savings(name):
    
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT savings FROM {name}""")
        savings =  cursor.fetchone()

        return savings[0] if savings is not None else 0

def update_total_expense(name):
        with connect_db(EXPENSE_FILE) as conn:
            cursor = conn.cursor()
    
            cursor.execute(f"""SELECT sum(expense) From "{name}" """)
            total_expenses = cursor.fetchone()[0]
    
            cursor.execute(f"""UPDATE "{name}" SET total_expenses = ?""", (total_expenses,))
            conn.commit()
    
def update_total_income(name):
     with connect_db() as conn:
          cursor = conn.cursor()

          cursor.execute(f"""SELECT sum(fixed_income) + sum(extra_income) From "{name}" """)
          total_income = cursor.fetchone()[0]

          cursor.execute(f"""UPDATE "{name}" SET total_income = ?""", (total_income,))
          conn.commit()

          return total_income
     
def store_extra_income(name,data):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""INSERT INTO "{name}" (extra_income) VALUES (?)""", (data,))
        conn.commit()
     
def timer():
     data = load_json(FIXED_DATA)
     for user in data:
        if data[user]['next_payment'] > datetime.datetime.now().strftime('%Y-%m-%d'):
            data[user]['next_payment'] = datetime.datetime.now() + datetime.timedelta(days=user['frequency'])
            add_savings(user, data[user]['saving_amount'])
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""INSERT INTO "{user}" (fixed_income) VALUES = ?""", (data[user]['fixed_income'],))
                conn.commit()
            
            save_json(FIXED_DATA,data)

def get_latest(name):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT * FROM {name} TIMESTAMP ORDER BY TIMESTAMP DESC LIMIT 1""")
        data =  cursor.fetchone()

        return data

def add_savings(name,add):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT savings FROM {name}""")
        saved = cursor.fetchone()

        new_savings = int(saved[0]) + int(add)

        cursor.execute(f"""UPDATE {name} SET savings = ?""",(new_savings,))

def add_expenses(name,item,value):
    with connect_db(EXPENSE_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"""INSERT INTO "{name}" (item,expense) VALUES (?,?)""", (item,value))
        conn.commit()

def add_item(name,add):
    with connect_db(EXPENSE_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"""INSERT INTO "{name}" (item) VALUES (?)""", (add,))
        conn.commit()

def get_expenses(name):
    with connect_db(EXPENSE_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT * FROM "{name}" """)
        expenses = cursor.fetchall()
        if expenses is None:
            return 0
        return expenses
    
def get_total_expenses(name):
    with connect_db(file=EXPENSE_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT total_expenses FROM "{name}" """)
        expenses = cursor.fetchone()
        
        if expenses is None:
            return 0
        return expenses[0] 

def get_total_income(name):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT total_income FROM "{name}" """)
        income = cursor.fetchone()
        
        if income is None:
            return 0
        return income[0]
    
def expense_database_tables(name):
    with connect_db(file=EXPENSE_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{name}" (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                item TEXT NOT NULL,
                expense REAL DEFAULT 0,
                total_expenses REAL DEFAULT 0
            )
        """)
print(get_total_expenses("mommy"))
print(get_total_income("mommy"))