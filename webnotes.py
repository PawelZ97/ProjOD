from flask import Flask, redirect, request, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = False  # debug local
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
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            if(registerNewUser()):
                return render_template("base.html", message="Poprawna rejestracja")
            else:
                return render_template("base.html", message="Hasła nie zgadzają się")
        else:
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
                return (render_template("login.html",
                        error="Niepoprawny login lub/i hasło"))
        else:
            return render_template("login.html")


@app.route('/zychp/webnotes/logout')
def logout():
    email = checkUserLogin()
    if (email):
        session.pop('email', None)
    return redirect('/zychp/webnotes/login')


@app.route('/zychp/webnotes/dashboard')
def dashboard():
    email = checkUserLogin()
    if (email):
        print(email)
        return render_template("dashboard.html", email=email)
    else:
        return redirect('/zychp/webnotes/login')


@app.route('/zychp/webnotes/addNote', methods=['GET', 'POST'])
def upload():
    email = checkUserLogin()
    if (email):
        return render_template("addNote.html", email=email)
    return render_template("base.html", message='Nie zalogowano.')


def doLogin():
    email = request.form['email']
    password = request.form['password']

    loggingUser = User.query.filter_by(email=email).first()
    if (loggingUser):
        if(loggingUser.password == password):
            session['email'] = email
            return email
        else:
            print("Wrong password")
            return False
    else:
        print("User do not exist")
        return False


def registerNewUser():
    email = request.form['email']
    password = request.form['password']
    repassword = request.form['repassword']

    if((User.query.filter_by(email=email).first()) is None):
        if(password == repassword):
            createdUser = User(email=email, password=password)
            db.session.add(createdUser)
            db.session.commit()
            print("Register succesful")
            return True
        else:
            print("Passwords not match")
            return False
    else:
        print("User exist")
        return False


def checkUserLogin():
    if(session):
        cookie_email = session['email']
        return cookie_email
    else:
        print("Brak ciastka")
        return False
