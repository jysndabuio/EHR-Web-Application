import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from datetime import datetime
from forms import RegisterForm


load_dotenv(override=True)

app = Flask(__name__)

# Secure Credentials 
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
secret_key = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{username}:{password}@localhost/EHR_DB_MODEL"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = secret_key

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum("admin", "user", "doctor"), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal = db.Column(db.String(20), nullable=False)
    control_number = db.Column(db.String(50), nullable=True)
    security_question = db.Column(db.String(100), nullable=False)
    security_answer = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'patient':
            return redirect(url_for('patient_dashboard'))
        elif session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'patient':
            return redirect(url_for('patient_dashboard'))
        elif session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role

            user.last_login = datetime.now()
            db.session.commit()

            if user.role == 'patient':
                return redirect(url_for('patient_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return render_template('patient_dashboard.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return render_template('doctor_dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        email = form.email.data
        role = form.role.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        street = form.street.data
        city = form.city.data
        postal = form.postal.data
        control_number = form.control_number.data
        security_question = form.security_question.data
        security_answer = form.security_answer.data

        # Create new user
        new_user = User(
            username=username,
            password=password,
            email=email,
            role=role,
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            street=street,
            city=city,
            postal=postal,
            control_number=control_number,
            security_question=security_question,
            security_answer=security_answer
        )

        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
