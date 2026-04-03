
from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "secret123"

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/home')
     return redirect('/login')
     
     @app.route('/login')   
     def login():
         return render_template('login.html')
     
     @app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html')
# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        location TEXT,
        salary TEXT,
        contact TEXT,
        education TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ================= SEND OTP =================
def send_otp(email, otp):
    sender = "tejaakashmalla@gmail.com"
    password = "atxypuvrqkkrgvyt"

    msg = MIMEText(f"Your OTP is {otp}")
    msg['Subject'] = "JobHunter OTP"
    msg['From'] = sender
    msg['To'] = email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

# ================= LOGIN =================
@app.route('/', methods=['GET', 'POST'])
def login():

    # 🔥 Already logged in → skip login
    if 'user' in session:
        return redirect('/home')

    if request.method == 'POST':
        email = request.form['email']

        otp = str(random.randint(1000, 9999))
        session['otp'] = otp
        session['email'] = email

        send_otp(email, otp)

        return render_template('verify.html')

    return render_template('login.html')

# ================= VERIFY =================
@app.route('/verify', methods=['POST'])
def verify():
    user_otp = request.form['otp']

    if user_otp == session.get('otp'):

        email = session.get('email')

        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()

        if not user:
            c.execute("INSERT INTO users (email) VALUES (?)", (email,))
            conn.commit()

        conn.close()

        session['user'] = email  # 🔥 save login

        return redirect('/home')

    else:
        return "Invalid OTP ❌"

# ================= HOME =================
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')

    return render_template('home.html')

# ================= PROFILE =================
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/')

    email = session.get('user')

    return render_template('profile.html', email=email)

# ================= ADD JOB =================
@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        salary = request.form['salary']
        contact = request.form['contact']
        education = request.form['education']

        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()

        c.execute("INSERT INTO jobs (title, location, salary, contact, education) VALUES (?, ?, ?, ?, ?)",
                  (title, location, salary, contact, education))

        conn.commit()
        conn.close()

        return redirect('/home')

    return render_template('add_job.html')

# ================= SEARCH =================
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect('/')

    recommended = []
    others = []

    if request.method == 'POST':
        location = request.form['location']
        education = request.form['education']

        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()

        c.execute("SELECT * FROM jobs WHERE location LIKE ?", ('%' + location + '%',))
        jobs = c.fetchall()

        conn.close()

        for job in jobs:
            job_edu = job[5].lower()

            if education.lower() in job_edu:
                recommended.append(job)
            else:
                others.append(job)

    return render_template('search.html', recommended=recommended, others=others)

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= RUN =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)