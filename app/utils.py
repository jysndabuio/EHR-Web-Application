from itsdangerous import URLSafeTimedSerializer
from flask import current_app

# Generate a secure token for password reset
def generate_password_reset_token(user, expires_in=3600):
    s = URLSafeTimedSerializer(current_app.config['TOKEN_SECRET_KEY'])
    return s.dumps({'user_id': user.id}, salt='password-reset-salt')

# Verify and decode the token
def verify_password_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(current_app.config['TOKEN_SECRET_KEY'])
    try:
        data = s.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None  # Token is invalid or expired
    return data.get('user_id')

def send_reset_email(email, reset_url):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f"To reset your password, click the following link: {reset_url}\nIf you didn't make this request, please ignore this email."
    mail.send(msg)
