from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime
from .models import User
from .forms import RegisterForm, PasswordResetForm
from . import db, bcrypt, mail
from .utils import verify_password_reset_token, generate_password_reset_token

bp = Blueprint('main', __name__)

# Define redirect_dashboard directly in routes.py
def redirect_dashboard(role):
    """ Helper function to redirect based on role """
    if role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('main.doctor_dashboard'))
    elif role == 'patient':
        return redirect(url_for('main.patient_dashboard'))
    return redirect(url_for('main.index'))

@bp.route('/')
def index():
    return render_template('home.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():

    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect_dashboard(current_user.role)
    

    role = request.args.get('role')
    if not role or role not in ['admin', 'doctor']:
        flash("Invalid role selected. Please select a role.")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, role=role).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect_dashboard(user.role)
        else:
            flash('Invalid username or password.')

    return render_template('login.html', role=role)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    form.role.data = 'doctor'  # Pre-set the role as "patient"

    if form.validate_on_submit():
        # Create a new User object with role set to "patient"
        new_user = User(
            username=form.username.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            email=form.email.data,
            role=form.role.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            contact_number=form.contact_number.data,
            age=form.age.data,
            gender=form.gender.data,
            id_card_number=form.id_card_number.data,
            license_number=form.license_number.data,
            home_address=form.home_address.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login', role='doctor'))

    return render_template('register.html', form=form)

@bp.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)
    return render_template('patient_dashboard.html')

@bp.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)
    return render_template('doctor_dashboard.html')

@bp.route('/account')
@login_required
def account():
    if current_user.role != 'doctor':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)
    return render_template('account.html')

@bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)
    return render_template('admin_dashboard.html')

@bp.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate token and send password reset email
            token = generate_password_reset_token(user)
            reset_url = url_for('main.password_reset', token=token, _external=True)
            send_reset_email(user.email, reset_url)
            flash('Password reset email sent. Please check your inbox.')
        else:
            flash('Email not found.')
    return render_template('password_reset_request.html', form=form)

def send_reset_email(email, reset_url):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f"To reset your password, click the following link: {reset_url}\nIf you didn't make this request, please ignore this email."
    mail.send(msg)


@bp.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # Verify the token
    user_id = verify_password_reset_token(token)
    if not user_id:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.login'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        # Update the user's password
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('password_reset.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
