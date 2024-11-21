# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField,DateTimeField,TextAreaField, DateField, PasswordField, SelectField, TelField, SubmitField, HiddenField, EmailField, IntegerField, RadioField
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
    country = StringField('Country', validators=[DataRequired()])
    id_card_number = StringField('ID number', validators=[
            DataRequired(), 
            Regexp(r'^\d{11}$', message='Please provide your 11-digit identification card number')
    ])
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
        Optional()
    ])
    password = PasswordField('New Password', validators=[
        Optional(),
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

class PatientForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    home_address = StringField('Home Address', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    birthdate = DateField('Birthday', format='%Y-%m-%d', validators=[Optional()])
    gender = RadioField('M/W/F', choices=[
            ('male', 'Male'), # 'male' is the value, 'Male' is the label
            ('female', 'Female'),
            ('other', 'Other')], 
            validators=[DataRequired()])
    ecd_name = StringField('Emergency Contact Name', validators=[Optional()])
    ecd_contact_number = StringField('Emergency Contact Number', validators=[Optional()])
    submit = SubmitField('Save')

class PatientUpdateForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    home_address = StringField('Home Address', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class VisitForm(FlaskForm):
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    doctor_id = HiddenField('Doctor ID', validators=[DataRequired()])
    visit_date = DateTimeField('Visit Date', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    visit_type = StringField('Visit Type', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional()])

class ObservationForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    code = StringField('Observation Code', validators=[DataRequired(), Length(max=100)])
    value = StringField('Value', validators=[Optional(), Length(max=50)])
    status = SelectField('Status', choices=[('registered', 'Registered'), ('preliminary', 'Preliminary'), ('final', 'Final')], validators=[Optional()])
    effectiveDateTime = DateTimeField('Effective DateTime', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')

class AllergyIntoleranceForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    substance = StringField('Substance', validators=[DataRequired(), Length(max=100)])
    clinical_status = SelectField('Clinical Status', choices=[('active', 'Active'), ('inactive', 'Inactive'), ('resolved', 'Resolved')], validators=[Optional()])
    verification_status = SelectField('Verification Status', choices=[('unconfirmed', 'Unconfirmed'), ('confirmed', 'Confirmed')], validators=[Optional()])
    severity = SelectField('Severity', choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], validators=[Optional()])

class MedicationStatementForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    medication = StringField('Medication', validators=[DataRequired(), Length(max=100)])
    dosage = StringField('Dosage', validators=[Optional(), Length(max=50)])
    status = SelectField('Status', choices=[('active', 'Active'), ('completed', 'Completed'), ('entered-in-error', 'Entered in Error'), ('intended', 'Intended')], validators=[Optional()])
    effectivePeriod_start = DateField('Effective Start Date', validators=[Optional()])
    effectivePeriod_end = DateField('Effective End Date', validators=[Optional()])

class ProcedureForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    code = StringField('Procedure Code', validators=[DataRequired(), Length(max=100)])
    status = SelectField('Status', choices=[('preparation', 'Preparation'), ('in-progress', 'In Progress'), ('completed', 'Completed'), ('entered-in-error', 'Entered in Error')], validators=[Optional()])
    performed_date = DateField('Performed Date', validators=[Optional()])
    performer_id = HiddenField('Performer ID', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

class VitalsForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    type = StringField('Vital Type', validators=[DataRequired(), Length(max=50)])
    value = StringField('Value', validators=[DataRequired(), Length(max=50)])
    unit = StringField('Unit', validators=[DataRequired(), Length(max=20)])
    date_recorded = DateTimeField('Date Recorded', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')

class MedicalHistoryForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired(), Length(max=100)])
    onset_date = DateField('Onset Date', validators=[Optional()])
    resolution_date = DateField('Resolution Date', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

class ImmunizationForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    vaccine_code = StringField('Vaccine Code', validators=[DataRequired(), Length(max=100)])
    status = SelectField('Status', choices=[('completed', 'Completed'), ('entered-in-error', 'Entered in Error'), ('not-done', 'Not Done')], validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()])
    lot_number = StringField('Lot Number', validators=[Optional(), Length(max=50)])
    site = StringField('Site', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional()])

class AppointmentForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    doctor_id = HiddenField('Doctor ID', validators=[DataRequired()])
    start = DateTimeField('Start Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    end = DateTimeField('End Time', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    status = SelectField('Status', choices=[('proposed', 'Proposed'), ('pending', 'Pending'), ('booked', 'Booked'), ('arrived', 'Arrived'), ('fulfilled', 'Fulfilled'), ('cancelled', 'Cancelled'), ('noshow', 'No Show')], validators=[Optional()])
    reason = TextAreaField('Reason', validators=[Optional(), Length(max=255)])
