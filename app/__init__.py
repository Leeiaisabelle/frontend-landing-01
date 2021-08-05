from flask import Flask, render_template, request
import sqlite3 as sql
import requests
import json 
from . import db
import os
from app.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
db.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')
	
@app.route('/login')
def login():
	return render_template('login.html')
	#return('Login Page Here')
@app.route('/register')
def register():
	return render_template('register.html')
	#return('Register Page here')
    
@app.route('/adduser', methods= ['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        uname = request.form.get('uname')
        psw = request.form.get('psw')
        db = get_db()
        cur = db.cursor()
        msg = None

        if not uname:
            msg = 'Username is required.'
        elif not psw:
            msg = 'Password is required.'
        elif cur.execute(
            'SELECT id FROM users WHERE username = ?', (uname,)
        ).fetchone() is not None:
            msg = f"User {uname} is already registered."

        if not msg:
            cur.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (uname, generate_password_hash(psw))
            )
            db.commit()
            msg = f"User {uname} created successfully"
        
        return render_template("result.html", msg=msg)

@app.route('/confirmlogin', methods= ['POST', 'GET'])
def confirmlogin():
    if request.method == 'POST':
        uname = request.form.get('uname')
        psw = request.form.get('psw')
        db = get_db()
        cur = db.cursor()
        msg = None
        user = cur.execute(
            'SELECT * FROM users WHERE username = ?', (uname,)
        ).fetchone()

        if user is None:
            msg = 'Incorrect username.'
        elif not check_password_hash(user['password'], psw):
            msg = 'Incorrect password.'

        if not msg:
            msg = "Login Successful"
        return render_template("result.html", msg=msg)

@app.route('/list')
def list():
   db = get_db()   
   cur = db.cursor()
   cur.execute("SELECT * FROM users")
   rows = cur.fetchall()
   return render_template("list.html",rows = rows)


@app.route('/analytics')
def analyze():
	return render_template('analytics.html')
	#return('Analytics will be here')
    

@app.route('/userauth')
def userauth():
    return render_template('userauth.html')

@app.route('/getjs/<jsvar>')
def get_jsvar(jsvar):
    data = {'client_id':os.getenv("CLIENT_ID"), 
            'client_secret':os.getenv("CLIENT_SECRET"), 
            'grant_type':'authorization_code',
            'code':jsvar,
            'redirect_uri':'http://18.219.26.170:5000/'
            }
    r = requests.post('https://accounts.spotify.com/api/token',data=data)
    
    s = json.loads(r.text)
    access_token = s['access_token']
    token_type = s['token_type']
    expires_in = s['expires_in']
    refresh_token = s['refresh_token']
    scope = s['scope']
    
    return render_template('refreshcode.html', headers=r.headers, access_token=access_token, token_type=token_type, expires_in=expires_in, refresh_token=refresh_token,scope=scope)
if __name__ == '__main__':
    app.run(debug=True)
