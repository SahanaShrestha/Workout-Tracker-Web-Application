from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = ''   # Replace with your MySQL password, if any
app.config['MYSQL_DB'] = 'flask_users'  # Change this to your database name

mysql = MySQL(app)

# Workout Tracker Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/workout_tracker')
def workout_tracker():
    if 'username' in session:
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM workout_history WHERE username = %s", (username,))
        workout_data = cur.fetchall()
        cur.close()
        return render_template('index.html', workout_data=workout_data, username=username)
    else:
        return redirect(url_for('login'))

@app.route('/add_workout', methods=['POST'])
def add_workout():
    if 'username' in session:
        username = session['username']
        date = request.form['date']
        exercise = request.form['exercise']
        sets = int(request.form['sets'])
        reps = int(request.form['reps'])
        weight = float(request.form['weight'])
        target_muscle = request.form['target_muscle']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO workout_history (username, date, exercise, sets, reps, weight, target_muscle) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (username, date, exercise, sets, reps, weight, target_muscle))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('workout_tracker'))  # Redirect back to workout tracker page
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT username, password FROM tbl_users WHERE username = '{username}'")
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for('workout_tracker'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO tbl_users (username, password) VALUES ('{username}', '{pwd}')")
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)