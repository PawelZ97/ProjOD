from flask import Flask, session, request, redirect, render_template, send_from_directory
import json, uuid, hashlib

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_PATH'] = "/zychp/"

@app.route('/zychp/webNotes/base') 
def baseTest():
    return render_template("base.html")


@app.route('/zychp/webNotes/register')
def registerTest():
    return render_template("register.html")


@app.route('/zychp/webNotes/login', methods=['GET', 'POST'])
def login():
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            if doLogin():
                return redirect("/zychp/webNotes/fileslist")
            else:
                return render_template("login.html", error="Niepoprawny login lub/i hasło")
        else:
            return render_template("login.html")


@app.route('/zychp/webNotes/logout')
def logout():
    username = checkUserLogin()
    if (username):
        session.pop('username',None)
        session.pop('uuid',None)
    return redirect('/zychp/webNotes/login')


@app.route('/zychp/webNotes/dashboard')
def dashboard():
    username = checkUserLogin()
    if (username):
        return render_template("dashboard.html", username=username)
    else:                  
        return redirect('/zychp/webNotes/login')
    

@app.route('/zychp/webNotes/addNote', methods=['GET', 'POST'])
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
        users_credentials[user_data['login']] =  user_data['password']      
    return users_credentials
