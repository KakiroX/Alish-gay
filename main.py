
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create users table if not exists
def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with get_db() as conn:
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         (username, password))
                conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return 'Username already exists'
        except Exception as e:
            return f'Error: {str(e)}'

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                     (username, password))
            user = c.fetchone()

        if user:
            session['username'] = username
            return redirect('/welcome')
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
