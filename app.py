import uuid
from pymongo import MongoClient
from flask import Flask, jsonify, request, session, redirect, render_template, make_response, flash, url_for
from passlib.hash import pbkdf2_sha256
import datetime

# =================== CONFIG SECTION =======================
client = MongoClient('localhost', 27017)
db = client.FlaskApp

app = Flask(__name__)
app.secret_key = "e<{rQT<@:I-NnH1.NVAWV|nj3iw`S,H@.VTl4*:3I%..F7)vBc,/1HA;qFd)#1("
app.permanent_session_lifetime = datetime.timedelta(days=365)


# =================== URL ROUTE SECTION =======================
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/user/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('register.html')
    return User().signup()


@app.route('/user/signout')
def signout():
    return User().signout()


@app.route('/user/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    return User().login()


# =================== USER MODEL SECTION =======================
class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        session.permanent = True

        return redirect(url_for('home'))

    def signup(self):
        print(request.form)

        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }

        # Encrypt the password
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # Check for existing email address
        if db.users.find_one({"email": user['email']}):
            flash("Email address already in use", "error")
            return redirect(url_for('signup'))

        if db.users.insert_one(user):
            return self.start_session(user)

        # return jsonify({"error": "Signup failed"}), 400
        flash("Signup failed", "error")
        return redirect(url_for('signup'))

    def signout(self):
        session.clear()
        flash("Successfully Signed Out!", "success")
        return redirect(url_for('home'))

    def login(self):

        user = db.users.find_one({
            "email": request.form.get('email')
        })

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)

        flash("Invalid login credentials", "error")
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
