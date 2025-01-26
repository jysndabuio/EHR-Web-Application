from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for, redirect
from flask_mail import Message
from . import mail

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_reset_email(user):
    token = user.set_reset_token()  # Set and get the token
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: {url_for('main.reset_password', token=token, _external=True)} 
                If you did not make this request, simply ignore this email and no changes will be made.
                '''
    mail.send(msg)

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