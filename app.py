from flask import Flask, render_template,request,url_for,redirect,make_response
from apscheduler.schedulers.background import BackgroundScheduler
from AuthBarn import *
from utils import *
from config import *


instance = Action(_dev_mode=False)
app = Flask(__name__)
    
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
            decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
            name = decoded['Username']

            users = load_json(FIXED_DATA)

            if name not in users:
                response = make_response(redirect(url_for('getting_started')))
                response.set_cookie('token',token,httponly=True)
                return response
            else:
                response = make_response(redirect(url_for('index')))
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
            expense_database_tables(username)
            return redirect(url_for('login'))
        else:
            return render_template("register.html", message = "Failed to register")
    return render_template("register.html")

@app.route('/stats', methods = ['GET','POST'])
def stats():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']

    balance = get_balance(name)
    data = get_savings(name)
    total_expense = get_total_expenses(name)
    total_income = get_total_income(name)
    
    return render_template("stats.html", balance = balance,savings=data,total_expenses=total_expense,total_income=total_income)
    
@app.route('/add', methods = ['GET','POST'])
def add():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']
    if request.method == "POST":
        extra_income = request.form['extra_income']
        savings_data = load_json(FIXED_DATA)

        percent = savings_data[f'{name}']['saving_percentage']

        saving_value = round(float(percent) * int(extra_income),0)
        store_extra_income(name,extra_income)
        add_savings(name,saving_value)
        if update_total_income(name):
            return render_template("add.html", message="Successfully Added Record!!")
        else:
            return render_template("add.html", message="Failed to Add Record!!")
        
    return render_template("add.html")

@app.route('/getting_started', methods = ['GET','POST'])
def getting_started():
    token = request.cookies.get('token')
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    name = decoded['Username']

    if request.method == 'POST':
        saving_percentage = request.form['saving_percentage']
        fixed_income = request.form['fixed_income']
        frequency = request.form['frequency']
        

        data = load_json(FIXED_DATA)
        date = datetime.datetime.now() + datetime.timedelta(days=int(frequency))

        data[name] = {
            'fixed_income': fixed_income,
            'saving_percentage': saving_percentage,
            'saving_amount': int(fixed_income) * float(saving_percentage),
            'frequency': int(frequency),
            'next_payment': date.strftime('%Y-%m-%d'),
        }
        if save_json(FIXED_DATA,data):
            return redirect(url_for('index'))
        else:
            return render_template("getting_started.html", message = "Failed to add record")
    return render_template("getting_started.html", message = "Successfully Added Record")

@app.route('/expense', methods=['POST','GET'])
def expense():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']
    if request.method == 'POST':
        expense_value = request.form['expense']
        item_name = request.form['item']
        if expense_value and item_name:
            add_expenses(name,item_name,expense_value)
            update_total_expense(name)

        return redirect(url_for('expense'))
    item = get_expenses(name)
    return render_template('expense.html', item = item)

scheduler = BackgroundScheduler()
scheduler.add_job(func=timer, trigger="interval", days=1)

if __name__ == "__main__":
    app.run(debug=True)