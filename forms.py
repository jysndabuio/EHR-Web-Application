# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TelField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')], validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    phone = TelField('Phone Number', validators=[DataRequired()])
    street = StringField('House Number, Street', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal = StringField('Postal Code', validators=[DataRequired()])
    control_number = StringField('ID number (for Doctors only)')
    security_question = SelectField('Security Question', choices=[
        ('pet_name', 'What is the name of your first pet?'),
        ('mother_maiden', 'What is your mother\'s maiden name?'),
        ('favorite_color', 'What is your favorite color?'),
        ('city_born', 'What city were you born in?'),
        ('high_school', 'What high school did you attend?')
    ], validators=[DataRequired()])
    security_answer = StringField('Answer', validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long"),
        Regexp(r'^(?=.*[A-Z])(?=.*\d)', message="Password must contain at least one uppercase letter and one number.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')
