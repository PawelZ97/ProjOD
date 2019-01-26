from flask import Flask, redirect, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import binascii
import os
import re

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = False  # debug local
app.config['SESSION_COOKIE_PATH'] = "/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/base')
def base():
    return render_template("base.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            repassword = request.form['repassword']

            if(checkEmail(email) and checkPassword(password) and checkPassword(repassword)):
                if((User.query.filter_by(email=email).first()) is None):
                    if(password == repassword):
                        createdUser = User(email=email, password=hash_password(password))
                        db.session.add(createdUser)
                        db.session.commit()
                        return render_template("base.html", message='Rejestracja poprawna')
                    else:
                        return render_template("register.html", passwordErr="Podane hasła nie są zgodne")
                else:
                    return render_template("register.html", emailErr="Email zajęty")
            else:
                return render_template("register.html", emailErr="Niepoprawne dane")
        else:
            return render_template("register.html")


@app.route('/changepassword', methods=['GET', 'POST'])
def changePassword():
    email = checkUserLogin()
    if (email):
        if request.method == 'POST':
            oldpassword = request.form['oldpassword']
            password = request.form['password']
            repassword = request.form['repassword']

            if(checkPassword(oldpassword) and checkPassword(password) and checkPassword(repassword)):
                loggingUser = User.query.filter_by(email=email).first()
                
                if(verify_password(loggingUser.password, oldpassword)):
                    if(password == repassword):
                        loggingUser.password = hash_password(password)
                        db.session.commit()
                        return render_template("base.html", message='Hasło zmienione')
                    else:
                        return render_template("changePassword.html", email=email, passwordErr="Podane nowe hasła nie są zgodne")
                else:
                    return render_template("changePassword.html", email=email, oldpasswordErr="Podane hasło nie jest poprawne")
            else:
                return render_template("changePassword.html", email=email, oldpasswordErr="Hasła nie zgodne z zaleceniami")
        else:
            return render_template("changePassword.html", email=email)
    else:
        return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            if(checkEmail(email) and checkPassword(password)):
                loggingUser = User.query.filter_by(email=email).first()
                if (loggingUser):
                    if(verify_password(loggingUser.password, password)):
                        session['email'] = email
                        return redirect('/dashboard')
            return (render_template("login.html", error="Niepoprawny login lub/i hasło"))
        else:
            return render_template("login.html")


@app.route('/logout')
def logout():
    email = checkUserLogin()
    if (email):
        session.pop('email', None)
    return redirect('/login')


@app.route('/')
@app.route('/dashboard')
def dashboard():
    email = checkUserLogin()
    if (email):
        print(email)
        return render_template("dashboard.html", email=email)
    else:
        return redirect('/login')


@app.route('/addNote', methods=['GET', 'POST'])
def upload():
    email = checkUserLogin()
    if (email):
        return render_template("addNote.html", email=email)
    return render_template("base.html", message='Nie zalogowano.')


def checkUserLogin():
    if(session):
        cookie_email = session['email']
        return cookie_email
    else:
        print("Brak ciastka")
        return False


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def checkEmail(email):
    return re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)


def checkPassword(password):
    return re.match('^[!-~]*$', password)
