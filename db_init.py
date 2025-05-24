import sqlite3

conn = sqlite3.connect('banking.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    bank TEXT,
    account_no TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    user_id INTEGER,
    balance REAL DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Create transactions table
c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
print("✅ Database initialized with users and accounts tables.")
