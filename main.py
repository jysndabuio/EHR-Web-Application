import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# Secure Credentials 
load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
secret_key = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{username}:{password}@localhost/EHR_DB_MODEL"
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal = db.Column(db.String(20), nullable=False)
    control_number = db.Column(db.String(50))
    security_question = db.Column(db.String(100), nullable=False)
    security_answer = db.Column(db.String(100), nullable=False)

def password_checker(password):
    pass

@app.route('/')
def index():

# Check if the user is already logged in
    if 'user_id' in session:
        # Redirect based on the role
        if session.get('role') == 'patient':
            return redirect(url_for('patient_dashboard'))  # Redirect to patient dashboard
        elif session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard'))  # Redirect to doctor dashboard
        
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Check if the user is already logged in
    if 'user_id' in session:
        # Redirect based on the role
        if session.get('role') == 'patient':
            return redirect(url_for('patient_dashboard'))  # Redirect to patient dashboard
        elif session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard'))  # Redirect to doctor dashboard
        

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Retrieve user from the database
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Successful login, set user session
            session['user_id'] = user.id    # Store user ID in session
            session['role'] = user.role      # Store user role in session

            # Successful login, redirect based on role
            if user.role == 'patient':
                return redirect(url_for('patient_dashboard'))  # Add a route for patient dashboard
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))  # Add a route for doctor dashboard
        else:
            flash('Invalid username or password.')

    # If method is GET or if login failed, show the login form
    role = request.args.get('role')  # Keep the role passed in the query parameter unneccesary
    return render_template('login.html', role=role)

@app.route('/patient_dashboard')
def patient_dashboard():
    # Optionally, you can check if the user is logged in and has the correct role
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return render_template('patient_dashboard.html')  # Create this template for patients

@app.route('/doctor_dashboard')
def doctor_dashboard():
    # Optionally, you can check if the user is logged in and has the correct role
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    return render_template('doctor_dashboard.html')  # Create this template for doctors


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        email = request.form['email']
        role = request.form['role']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        phone = request.form['phone']
        street = request.form['street']
        city = request.form['city']
        postal = request.form['postal']
        control_number = request.form.get('control_number')
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']

        # Create new user
        new_user = User(
            username=username,
            password=password,
            email=email,
            role=role,
            first_name=first_name,
            last_name=last_name,
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
        return redirect(url_for('login', role=role))  # Redirect after registration

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('role', None)      # Remove user role from session
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))  # Redirect to login page


if __name__ == '__main__':
    with app.app_context():  # Create application context
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
