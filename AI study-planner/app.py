from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from g4f.client import Client

app = Flask(__name__)

# Database Configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduplanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(50), nullable=False)

class AIPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    plan_text = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        task_name = request.form.get('task_name')
        task_priority = request.form.get('priority')
        if task_name and task_priority:
            new_task = Task(name=task_name, priority=task_priority)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('dashboard'))
            
    all_tasks = Task.query.all()
    latest_plan = AIPlan.query.order_by(AIPlan.id.desc()).first()
    return render_template('dashboard.html', tasks=all_tasks, plan=latest_plan)

# 🚀 ORIGINAL G4F GENERATOR ROUTE
@app.route('/generate_ai_plan', methods=['POST'])
def generate_ai_plan():
    subject = request.form.get('subject')
    days = request.form.get('days')
    
    if subject and days:
        try:
            # g4f client initialization
            client = Client()
            prompt = f"Create a short step-by-step study plan for '{subject}' to be completed in {days} days. Give simple daily targets in bullet points."
            
            # g4f call
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
            )
            ai_response = response.choices[0].message.content
            
        except Exception as e:
            ai_response = f"⚠️ g4f Provider Error: Server overload hai. Thodi der baad fir se Generate dabaayein!\n\nDetails: {str(e)}"

        # Response ko database me hamesha ke liye save kar rahe hain
        new_plan = AIPlan(subject=subject, days=int(days), plan_text=ai_response)
        db.session.add(new_plan)
        db.session.commit()
            
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete_task(id):
    task_to_delete = Task.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    print("EduPlanner Server with g4f chalu ho raha hai...")
    # debug=False kiya hai taaki g4f background threads crash na karein
    app.run(debug=False, port=5000)