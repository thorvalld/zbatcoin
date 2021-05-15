from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from conf import _mysql_host, _mysql_user, _mysql_password, _mysql_database, _mysql_cursor_class, _secret_key
from sqlhelper import *
from forms import *
from functools import wraps

app = Flask(__name__)

app.config['MYSQL_HOST'] = _mysql_host
app.config['MYSQL_USER'] = _mysql_user
app.config['MYSQL_PASSWORD'] = _mysql_password
app.config['MYSQL_DB'] = _mysql_database
app.config['MYSQL_CURSORCLASS'] = _mysql_cursor_class

mysql = MySQL(app)


def login_user(username):
    users = Table('users', 'name', 'username', 'email', 'password')
    user = users.fetch_one("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('unauthorized', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route("/")
def index():
    transfer_funds('BANK', 'tester_user', 3000)
    return render_template('index.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table('users', 'name', 'username', 'email', 'password')
    if request.method == 'POST':
        username_ = form.username.data
        email_ = form.email.data
        fname_ = form.name.data

        if is_new_user(username_):
            password_ = sha256_crypt.hash(str(form.password.data))
            users.insert(fname_, username_, email_, password_)
            login_user(username_)
            return redirect(url_for('dashboard'))
        else:
            # flash('user already exists', 'danger')
            return redirect(url_for('/'))

    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        candidate_password = request.form['password']

        users = Table('users', 'name', 'username', 'email', 'password')
        user = users.fetch_one('username', username)
        access_password = user.get('password')

        if access_password is None:
            flash('username is not found', 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(candidate_password, access_password):
                login_user(username)
                flash('logged in successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('invalid username/password', 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('logged out successfully', 'success')
    return redirect(url_for('login'))


@app.errorhandler(404)
def not_found(e):
    return render_template('page_not_found.html'), 404


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html', session=session)


@app.route('/transaction', methods=['GET', 'POST'])
@is_logged_in
def transaction():
    form = TransferFundsForm(request.form)
    get_balance = fetch_balance(session.get('username'))
    current_balance = 0.00
    if get_balance > 0:
        current_balance = get_balance

    if request.method == 'POST':
        try:
            transfer_funds(session.get('username'), form.username.data, form.amount.data)
            flash('Funds transferred', 'success')
        except Exception as exc:
            flash(str(exc), 'danger')
        return redirect(url_for('transaction'))

    return render_template('transaction.html', balance=current_balance, form=form)


@app.route('/buy', methods=['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyFundsForm(request.form)
    balance = fetch_balance(session.get('username'))
    if request.method == 'POST':
        try:
            transfer_funds('BANK', session.get('username'), form.amount.data)
            flash('Purchase successful', 'success')
        except Exception as exc:
            flash(str(exc), 'danger')
        return redirect(url_for('transaction'))

    return render_template('buy.html', balance=balance, form=form)


if __name__ == '__main__':
    app.secret_key = _secret_key
    app.run(debug=True)
