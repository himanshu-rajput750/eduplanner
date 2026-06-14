from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyplanner.db'

db = SQLAlchemy(app)

# ---------------- DATABASE ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200))
    priority = db.Column(db.Integer)

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        user = User(
            username=username,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(
        username=username,
        password=password
    ).first()

    if user:
        return redirect('/dashboard')

    return "Invalid Login"

@app.route('/dashboard')
def dashboard():

    tasks = Task.query.all()

    return render_template(
        'dashboard.html',
        tasks=tasks
    )

@app.route('/add_task', methods=['POST'])
def add_task():

    task_name = request.form['task']
    priority = request.form['priority']

    task = Task(
        task_name=task_name,
        priority=priority
    )

    db.session.add(task)
    db.session.commit()

    return redirect('/dashboard')

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)