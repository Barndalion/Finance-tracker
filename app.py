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

    balance = get_balance(name)
    data = get_latest(name)
    
    if not data:  
        return render_template("stats.html", balance=0, savings=0, projected=0)
    
    return render_template("stats.html", balance = balance,savings=data[4],projected=0)
    
@app.route('/add', methods = ['GET','POST'])
def add():
    token = request.cookies.get('token')
    decoded = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    name = decoded['Username']
    if request.method == "POST":
        extra_income = request.form['extra_income']
        update(name)
        if add_record(name,extra_income):
            return render_template("add.html", message="Successfully Added Record!!")
        else:   
            return render_template("add.html", message="Failed to add record")
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
            'saving_amount': int(fixed_income) * float(saving_percentage),
            'frequency': frequency,
            'next_payment': datetime.datetime.now() + datetime.timedelta(days=int(frequency)),
        }
        if save_json(FIXED_DATA,data):
            return redirect(url_for('index'))
        else:
            return render_template("getting_started.html", message = "Failed to add record")
    return render_template("getting_started.html", message = "Successfully Added Record")

scheduler = BackgroundScheduler()
scheduler.add_job(func=timer, trigger="interval", days=1)

if __name__ == "__main__":
    app.run(debug=True)