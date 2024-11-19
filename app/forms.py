# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, SelectField, TelField, SubmitField, HiddenField, EmailField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange, Optional

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = HiddenField(default='doctor')  # Set role as hidden with default "patient"
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    birthday = DateField('Birthday', format='%Y-%m-%d', validators=[Optional()])
    gender = RadioField('M/W/F', choices=[
            ('male', 'Male'), # 'male' is the value, 'Male' is the label
            ('female', 'Female'),
            ('other', 'Other')], 
            validators=[DataRequired()])
    contact_number=IntegerField(validators=[DataRequired()])
    id_card_number = StringField('ID number', validators=[
            DataRequired(), 
            Regexp(r'^\d{11}$', message='Please provide your 11-digit identification card number')
    ])
    license_number=IntegerField('License Number', validators=[DataRequired()])
    home_address=StringField('Complete Home Adress', validators=[DataRequired()]) 
    password = PasswordField('Password', validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
            Regexp(r'^(?=.*[A-Z])(?=.*\d)', message="Password must contain at least one uppercase letter and one number.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
            DataRequired(),
            EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Save Changes')



class UserUpdateProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact_number=IntegerField(validators=[DataRequired()])
    country = StringField('Country', validators=[Optional()])
    home_address=StringField('Complete Home Adress', validators=[DataRequired()]) 
    med_deg = StringField('Medical Degree', validators=[Optional()])
    med_deg_spec = StringField('Specialization', validators=[Optional()])
    board_cert = StringField('Board Certification', validators=[Optional()])
    license_number=IntegerField('License Number', validators=[DataRequired()])
    license_issuer = StringField('License Issuer', validators=[Optional()])
    license_expiration = DateField('License Expiration', validators=[Optional()])
    years_of_experience = StringField('Years of Experience', validators=[Optional()])
    ecd_name = StringField('Emergency Contact Name', validators=[Optional()])
    ecd_contact_number = StringField('Emergency Contact Number', validators=[Optional()])

    current_password = PasswordField('Current Password', validators=[
        Optional(),  # Current password is optional unless changing the password
    ])
    password = PasswordField('New Password', validators=[
        Optional(),  # New password is optional for profile updates
        Length(min=8, message="Password must be at least 8 characters long"),
        Regexp(r'^(?=.*[A-Z])(?=.*\d)', message="Password must contain at least one uppercase letter and one number.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

class PasswordResetForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password') 