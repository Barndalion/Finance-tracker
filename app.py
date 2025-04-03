from flask import Flask, render_template,request,url_for,redirect,make_response
from AuthBarn import *
import json
import os
import datetime 
from config import create_table, connect_db, FIXED_DATA, load_json, save_json,update

instance = Action(_dev_mode=False)
app = Flask(__name__)
    
def get_latest(name):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT * FROM {name} ORDER BY timestamp DESC LIMIT 1""")
        data =  cursor.fetchone()

        return data
    
def get_balance(name):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT balance FROM {name} ORDER BY timestamp DESC LIMIT 1""")
        data =  cursor.fetchone()

        return data
    
def add_record(name,fixed_income,expense,saving,extra_income):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {name} (fixed_income,expense,savings,extra_income) VALUES (?,?,?,?)",(fixed_income,expense,saving,extra_income))
        conn.commit()
    return True
    
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        
        log = instance.login(username,password)
        if log['state']:
            token = log['token']

            response = make_response(redirect(url_for('getting_started')))
            response.set_cookie('token',token,httponly=True)
            return response
        else:
            return render_template("login.html", message = "Failed to log in")
    return render_template("login.html")

@app.route('/index', methods = ['GET','POST'])
def index():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']
    return render_template("index.html", name = name)

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        if instance.register(username,password):
            create_table(username)
            return redirect(url_for('login'))
        else:
            return render_template("register.html", message = "Failed to register")
    return render_template("register.html")

@app.route('/stats', methods = ['GET','POST'])
def stats():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']

    data = get_latest(name)
    
    if not data:  
        return render_template("stats.html", balance=0, savings=0, projected=0)
    
    return render_template("stats.html", balance = data[1],savings=data[4],projected=0)
    
@app.route('/add', methods = ['GET','POST'])
def add():
    data = load_json(FIXED_DATA)
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']
    if request.method == "POST":
        fixed_income = request.form['fixed_income']
        expense = request.form['expense']
        extra_income = request.form['extra_income']

        update(name)
        saving = data[name]['saving_percentage'] * fixed_income
        if add_record(name,fixed_income,expense,saving,extra_income):
            return render_template("add.html", message="Successfully Added Record!!")
    return render_template("add.html")

@app.route('/getting_started', methods = ['GET','POST'])
def getting_started():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']

    if request.method == 'POST':
        saving_percentage = request.form['saving_percentage']
        fixed_income = request.form['fixed_income']
        frequency = request.form['frequency']

        data = load_json(FIXED_DATA)

        data[name] = {
            'fixed_income': fixed_income,
            'saving_percentage': saving_percentage,
            'frequency': frequency
        }
        save_json(FIXED_DATA,data)

        return render_template("getting_started.html", message = "Successfully Added Record")
    return render_template("getting_started.html", message = "Successfully Added Record")


if __name__ == "__main__":
    app.run(debug=True)