from config import connect_db, FIXED_DATA, load_json, save_json
import json
import datetime

def get_balance(name):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT total_income FROM {name}""")
        total_income =  cursor.fetchone()

        cursor.execute(f"""SELECT total_expenses FROM {name}""")
        total_expenses =  cursor.fetchone()
        if total_income and total_expenses is not None:
            balance = total_income[0] - total_expenses[0]
        else:
            balance = 0
        
        return balance
    
def update(name):
     with connect_db() as conn:
          cursor = conn.cursor()

          cursor.execute(f"""SELECT sum(fixed_income) + sum(extra_income) From "{name}" """)
          total_income = cursor.fetchone()[0]

          cursor.execute(f"""UPDATE "{name}" SET total_income = ?""", (total_income,))
          conn.commit()

          return total_income
     
def timer():
     data = load_json(FIXED_DATA)
     for user in data:
        if data[user]['next_payment'] > datetime.datetime.now():
            data[user]['next_payment'] = datetime.datetime.now() + datetime.timedelta(days=user['frequency'])
            savings(user, data[user]['saving_amount'])
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
    
def add_record(name,extra_income):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {name} (extra_income) VALUES = ?",(extra_income,))
        conn.commit()
    return True

def savings(name,add):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT savings FROM {name}""")
        saved = cursor.fetchone()

        new_savings = saved + add

        cursor.execute(f"""UPDATE {name} SET savings = ?""",(new_savings,))
        