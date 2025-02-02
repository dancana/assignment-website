# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3, os, random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'database.db'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database (run once or check on startup)
def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    # Create a table for users
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        paid INTEGER DEFAULT 0
                    )''')
    # Create a table for assignments (file metadata)
    cur.execute('''CREATE TABLE IF NOT EXISTS assignments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        filepath TEXT
                    )''')
    conn.commit()
    conn.close()

init_db()

# Helper function to get DB connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home page – list features if logged in
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', paid=session.get('paid', 0))
    else:
        return redirect(url_for('login'))

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'error')
        finally:
            conn.close()
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['paid'] = user['paid']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

# Upload assignments (only accessible if logged in and paid)
# Updated assignments route in app.py
@app.route('/assignments', methods=['GET', 'POST'])
def assignments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()

    # Process file upload only if the request is POST and the user is admin
    if request.method == 'POST':
        if session.get('username') != 'admin':
            flash('Only the admin can upload files.', 'error')
            return redirect(url_for('assignments'))
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        conn.execute("INSERT INTO assignments (filename, filepath) VALUES (?, ?)", (file.filename, filepath))
        conn.commit()
        flash('File uploaded successfully', 'success')
    
    assignments = conn.execute("SELECT * FROM assignments").fetchall()
    conn.close()
    return render_template('assignments.html', assignments=assignments)


# Download assignment file
@app.route('/download/<int:file_id>')
def download(file_id):
    if 'user_id' not in session or session.get('paid', 0) == 0:
        flash('Please login and complete payment to download files.', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    file = conn.execute("SELECT * FROM assignments WHERE id=?", (file_id,)).fetchone()
    conn.close()
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file['filename'], as_attachment=True)
    else:
        flash('File not found', 'error')
        return redirect(url_for('assignments'))

# Payment page (simulate payment for Mpesa and PayPal)
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # In a real-world scenario, here you would integrate with Mpesa/PayPal APIs.
        # For simulation, we assume the user pays 10 KSH successfully.
        payment_method = request.form.get('payment_method')
        # Simulate payment validation...
        if payment_method in ['mpesa', 'paypal']:
            conn = get_db_connection()
            conn.execute("UPDATE users SET paid=1 WHERE id=?", (session['user_id'],))
            conn.commit()
            conn.close()
            session['paid'] = 1
            flash('Payment successful! You now have access.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid payment method', 'error')
    return render_template('payment.html')

@app.route('/setup_admin')
def setup_admin():
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password, paid) VALUES (?, ?, ?)", ('admin', 'yourChosenPassword', 1))
        conn.commit()
        return "Admin user created with password 'yourChosenPassword'."
    except sqlite3.IntegrityError:
        return "Admin user already exists."
    finally:
        conn.close()


@app.route('/admin')
def admin_dashboard():
    # Check if the user is logged in and is admin
    if 'user_id' not in session or session.get('username') != 'admin':
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    
    # If you later add an "activities" table, you could also fetch activities here:
    # activities = conn.execute("SELECT * FROM activities ORDER BY timestamp DESC").fetchall()
    
    conn.close()
    return render_template('admin.html', users=users)


# Quiz game page – only accessible if paid
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session or session.get('paid', 0) == 0:
        flash('Please complete payment to access the quiz game.', 'error')
        return redirect(url_for('payment'))
    
    # Sample quiz question. In a real project, questions could come from a database.
    question = {
        'text': "What is the capital of France?",
        'choices': ['Paris', 'Berlin', 'Rome', 'Madrid'],
        'answer': 'Paris'
    }
    ai_choice = random.choice(question['choices'])  # Simulate Python AI random answer

    user_answer = None
    result = None
    if request.method == 'POST':
        user_answer = request.form.get('choice')
        if user_answer:
            if user_answer == question['answer']:
                result = "You answered correctly!"
            else:
                result = f"Incorrect! The correct answer is {question['answer']}."
    return render_template('quiz.html', question=question, ai_choice=ai_choice, user_answer=user_answer, result=result)

if __name__ == '__main__':
    app.run(debug=True)
