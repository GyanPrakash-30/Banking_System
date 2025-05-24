from db import get_db

def log_transaction(user_id, txn_type, amount, details):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, type, amount, details) VALUES (?, ?, ?, ?)",
        (user_id, txn_type, amount, details)
    )
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()
    conn.close()
    return balance[0] if balance else 0

def deposit(user_id, amount):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    log_transaction(user_id, "Deposit", amount, "Self deposit")

def withdraw(user_id, amount):
    if get_balance(user_id) < amount:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    log_transaction(user_id, "Withdraw", amount, "Self withdrawal")
    return True

def transfer(from_user, to_username, amount):
    conn = get_db()
    cursor = conn.cursor()

    # Get recipient ID
    cursor.execute("SELECT id FROM users WHERE username = ?", (to_username,))
    to_user = cursor.fetchone()
    if not to_user:
        return "Recipient not found"
    to_user_id = to_user[0]

    # Check balance
    if get_balance(from_user) < amount:
        conn.close()
        return "Insufficient funds"

    # Perform transfer
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", (amount, from_user))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ?", (amount, to_user_id))
    conn.commit()

    # Get usernames for logging
    cursor.execute("SELECT username FROM users WHERE id = ?", (from_user,))
    from_username = cursor.fetchone()[0]
    cursor.execute("SELECT username FROM users WHERE id = ?", (to_user_id,))
    to_username_real = cursor.fetchone()[0]
    conn.close()

    # Log both sides
    log_transaction(from_user, "Transfer", amount, f"To {to_username_real}")
    log_transaction(to_user_id, "Transfer", amount, f"From {from_username}")
    return "Success"

def pay_bill(user_id, amount, biller):
    if get_balance(user_id) < amount:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    log_transaction(user_id, "Bill Payment", amount, f"Biller: {biller}")
    return True

def get_transaction_history(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions
