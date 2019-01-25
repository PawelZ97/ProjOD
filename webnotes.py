from flask import Flask, redirect, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import uuid
import json


app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_PATH'] = "/zychp/webnotes"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    
   
@app.route('/zychp/webnotes/base') 
def baseTest():
    return render_template("base.html")


@app.route('/zychp/webnotes/register', methods=['GET', 'POST'])
def registerTest():
    return render_template("register.html")


@app.route('/zychp/webnotes/login', methods=['GET', 'POST'])
def login():
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            if doLogin():
                return redirect("/zychp/webnotes/dashboard")
            else:
                return render_template("login.html", error="Niepoprawny login lub/i hasło")
        else:
            return render_template("login.html")


@app.route('/zychp/webnotes/logout')
def logout():
    username = checkUserLogin()
    if (username):
        session.pop('username', None)
        session.pop('uuid', None)
    return redirect('/zychp/webnotes/login')


@app.route('/zychp/webnotes/dashboard')
def dashboard():
    username = checkUserLogin()
    if (username):
        return render_template("dashboard.html", username=username)
    else:                  
        return redirect('/zychp/webnotes/login')
    

@app.route('/zychp/webnotes/addNote', methods=['GET', 'POST'])
def upload():
    username = checkUserLogin()
    if (username):
        return render_template("addNote.html", username=username)
    return render_template("base.html", message='Nie zalogowano.')


def doLogin():
    username = request.form['username']
    users_credentials = getUsersCredentials()

    for user in users_credentials:
        hashpass = hashlib.sha256(request.form['password'].encode()).hexdigest()
        if username == user and hashpass == users_credentials[user]:
            user_uuid = str(uuid.uuid4())
            session['username'] = username
            session['uuid'] = user_uuid
            return True
    return False


def checkUserLogin():
    users_credentials = getUsersCredentials()
    if(session):
        cookie_username = session['username']
        if cookie_username in users_credentials:
            return cookie_username
        else:
            print("Brak loginu w bazie")
            return False
    else:
        print("Brak ciastka")
        return False


def getUsersCredentials():
    dbfile = open('database.json', 'r')
    database = json.loads(dbfile.read())
    users_credentials = {}
    for user_data in database['userslist']:
        users_credentials[user_data['login']] = user_data['password']
    return users_credentials
