from flask import Flask, jsonify, session, redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import (
    get_balance, deposit, withdraw, transfer, pay_bill,
    get_transaction_history
)
from db import get_db
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect('/dashboard')
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        bank = request.form['bank']
        account_no = request.form['account_no']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return "Username already exists", 400

        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return "Email already in use", 400

        try:
            cursor.execute("""
                INSERT INTO users (name, gender, email, phone, address, bank, account_no, username, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, gender, email, phone, address, bank, account_no, username, password))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO accounts (user_id, balance) VALUES (?, 0)", (user_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            return "Registration failed", 400
        finally:
            conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone, address, bank, account_no FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    user_data = {
        'name': user[0],
        'email': user[1],
        'phone': user[2],
        'address': user[3],
        'bank': user[4],
        'account_no': user[5]
    }

    balance = get_balance(user_id)

    txns = get_transaction_history(user_id)
    transactions = [
        {'type': t[2], 'amount': t[3], 'details': t[4], 'timestamp': t[5]}
        for t in txns
    ]

    return render_template(
        'dashboard.html',
        balance=balance,
        user=user_data,
        transactions=transactions
    )

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    email = request.form['email']
    phone = request.form['phone']
    new_password = request.form['password']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ?, phone = ? WHERE id = ?", (email, phone, user_id))
    if new_password:
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    if 'user_id' not in session:
        return jsonify(success=False, error="Not logged in"), 401
    try:
        amount = float(request.json['amount'])
        deposit(session['user_id'], amount)
        return jsonify(success=True, balance=get_balance(session['user_id']))
    except Exception as e:
        print("Deposit error:", e)
        return jsonify(success=False, error="Server error"), 500

@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    if 'user_id' not in session:
        return jsonify(success=False, error="Not logged in"), 401
    try:
        amount = float(request.json['amount'])
        if withdraw(session['user_id'], amount):
            return jsonify(success=True, balance=get_balance(session['user_id']))
        else:
            return jsonify(success=False, error="Insufficient funds")
    except Exception as e:
        print("Withdraw error:", e)
        return jsonify(success=False, error="Server error"), 500

@app.route('/api/transfer', methods=['POST'])
def api_transfer():
    if 'user_id' not in session:
        return jsonify(success=False, error="Not logged in"), 401
    try:
        to = request.json['to']
        amount = float(request.json['amount'])
        result = transfer(session['user_id'], to, amount)
        if result == "Success":
            return jsonify(success=True, balance=get_balance(session['user_id']))
        else:
            return jsonify(success=False, error=result)
    except Exception as e:
        print("Transfer error:", e)
        return jsonify(success=False, error="Server error"), 500

@app.route('/api/bill', methods=['POST'])
def api_bill():
    if 'user_id' not in session:
        return jsonify(success=False, error="Not logged in"), 401
    try:
        amount = float(request.json['amount'])
        biller = request.json['biller']
        if pay_bill(session['user_id'], amount, biller):
            return jsonify(success=True, balance=get_balance(session['user_id']))
        else:
            return jsonify(success=False, error="Insufficient funds")
    except Exception as e:
        print("Bill payment error:", e)
        return jsonify(success=False, error="Server error"), 500

@app.route('/api/history')
def api_transaction_history():
    if 'user_id' not in session:
        return jsonify(success=False, error="Not logged in"), 401
    txns = get_transaction_history(session['user_id'])
    transactions = [
        {'timestamp': t[5], 'type': t[2], 'amount': t[3], 'details': t[4]}
        for t in txns
    ]
    return jsonify(success=True, transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)
