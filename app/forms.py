# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField,FormField,FieldList,DateTimeField,TextAreaField, DateField, PasswordField, SelectField, TelField, SubmitField, HiddenField, EmailField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange, Optional
from datetime import date
from .models import MedicationStatement, Observation

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

class MedicationStatementForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    medication_code = StringField('Medication Code', validators=[DataRequired(), Length(max=100)])
    medication_name = StringField('Medication Name', validators=[DataRequired(), Length(max=255)])
    status = SelectField('Status', choices=[], validators=[DataRequired()])  # Empty choices, will be populated dynamically
    effectivePeriod_start = DateField('Start Date', validators=[Optional()])
    effectivePeriod_end = DateField('End Date', validators=[Optional()])
    date_asserted = DateField('Date Asserted', validators=[Optional()])  # Date the statement was made
    information_source = StringField('Information Source', validators=[Optional(), Length(max=255)])  # Who reported
    adherence = SelectField('Adherence', choices=[], validators=[Optional()])  # Empty choices, will be populated dynamically
    reason_code = TextAreaField('Reason Code', validators=[Optional()])
    reason_reference = StringField('Reason Reference', validators=[Optional(), Length(max=100)])  # Reference to Condition/Observation
    status_reason = StringField('Status Reason', validators=[Optional(), Length(max=255)])  # Reason for status change
    dosage_instruction = TextAreaField('Dosage Instruction', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    category = SelectField('Category', choices=[], validators=[Optional()])  # Empty choices, will be populated dynamically
    route_of_administration = StringField('Route of Administration', validators=[Optional(), Length(max=100)])  # e.g., "oral", "IV"
    timing = StringField('Timing', validators=[Optional(), Length(max=100)])  # e.g., "twice daily"

    # Dynamically set the choices for the fields in the form constructor
    def __init__(self, *args, **kwargs):
        super(MedicationStatementForm, self).__init__(*args, **kwargs)
        
        # Dynamically populate choices for status
        self.status.choices = [(status['code'], status['display']) for status in MedicationStatement.get_status_codes()]

        # Dynamically populate choices for adherence
        self.adherence.choices = [(adherence['code'], adherence['display']) for adherence in MedicationStatement.get_adherence_codes()]

        # Dynamically populate choices for category
        self.category.choices = [
            ('outpatient', 'Outpatient'),
            ('inpatient', 'Inpatient'),
            ('virtual', 'Virtual')
        ]


class VisitForm(FlaskForm):
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    doctor_id = HiddenField('Doctor ID', validators=[DataRequired()])
    visit_date = DateTimeField('Visit Date', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    visit_type = StringField('Visit Type', validators=[Optional(), Length(max=50)])
    medications = FieldList(FormField(MedicationStatementForm), min_entries=1, max_entries=10)
    notes = TextAreaField('Notes', validators=[Optional()])

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length
from datetime import datetime

class ObservationForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    code = StringField('Observation Code', validators=[DataRequired(), Length(max=100)])  # LOINC or SNOMED code
    value = StringField('Observation Value', validators=[Optional(), Length(max=255)])  # Value of the observation
    status = SelectField('Status', choices=[], validators=[DataRequired()])  # Empty choices, will be populated dynamically
    category = SelectField('Category', choices=[], validators=[Optional()])  # Empty choices, will be populated dynamically
    effectiveDateTime = DateTimeField('Effective Date/Time', validators=[Optional()], default=datetime.utcnow)  # Date/Time of observation

    # Dynamically set the choices for the fields in the form constructor
    def __init__(self, *args, **kwargs):
        super(ObservationForm, self).__init__(*args, **kwargs)
        
        # Dynamically populate choices for status
        self.status.choices = [(status['code'], status['display']) for status in Observation.get_status_options()]
        # Dynamically populate choices for status
    
        
        # Dynamically populate choices for category
        # Dynamically populate choices for status
        self.category.choices = [(status['code'], status['display']) for status in Observation.get_category_options()]
        
        # Dynamically populate choices for code
        self.code.choices = [(status['code'], status['display']) for status in Observation.get_code_options()]




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

class AllergyIntoleranceForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    substance = StringField('Substance', validators=[DataRequired(), Length(max=100)])
    clinical_status = SelectField('Clinical Status', choices=[], validators=[Optional()])
    verification_status = SelectField('Verification Status', choices=[], validators=[Optional()])
    severity = SelectField('Severity', choices=[], validators=[Optional()])
    category = SelectField('Category', choices=[], validators=[Optional()])
    reaction = TextAreaField('Reaction', validators=[Optional()])
    onset = DateField('Onset Date', validators=[Optional()])

     # Dynamically set the choices for clinical_status, verification_status, severity, and category
    #form.clinical_status.choices = [(status['code'], status['display']) for status in AllergyIntolerance.get_clinical_status_codes()]
    #form.verification_status.choices = [(status['code'], status['display']) for status in AllergyIntolerance.get_verification_status_codes()]
    #form.severity.choices = [(level['code'], level['display']) for level in AllergyIntolerance.get_severity_levels()]
    #form.category.choices = [(category['code'], category['display']) for category in AllergyIntolerance.get_category_options()]



class ImmunizationForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    vaccine_code = SelectField('Vaccine Code', choices=[], validators=[DataRequired()])  # Empty choices initially
    status = SelectField('Status', choices=[], validators=[Optional()])  # Empty choices initially
    date = DateField('Date', validators=[DataRequired()])
    lot_number = StringField('Lot Number', validators=[Optional(), Length(max=50)])
    site = SelectField('Site', choices=[], validators=[Optional()])  # Empty choices initially
    route = SelectField('Route', choices=[], validators=[Optional()])  # Empty choices initially
    dose_quantity = StringField('Dose Quantity', validators=[Optional(), Length(max=20)])  # Added dose quantity
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional()])

    # Dynamically set the choices for the vaccine_code, status, site, and route fields
    #form.vaccine_code.choices = [(vaccine['code'], vaccine['display']) for vaccine in Immunization.get_vaccine_codes()]
    #form.status.choices = [(status['code'], status['display']) for status in Immunization.get_status_codes()]
    #form.site.choices = [(site['code'], site['display']) for site in Immunization.get_site_options()]
    #form.route.choices = [(route['code'], route['display']) for route in Immunization.get_route_options()]


class MedicalHistoryForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired(), Length(max=100)])
    onset_date = DateField('Onset Date', validators=[Optional()])
    resolution_date = DateField('Resolution Date', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])


class AppointmentForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    doctor_id = HiddenField('Doctor ID', validators=[DataRequired()])
    start = DateTimeField('Start Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    end = DateTimeField('End Time', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    status = SelectField('Status', choices=[('proposed', 'Proposed'), ('pending', 'Pending'), ('booked', 'Booked'), ('arrived', 'Arrived'), ('fulfilled', 'Fulfilled'), ('cancelled', 'Cancelled'), ('noshow', 'No Show')], validators=[Optional()])
    reason = TextAreaField('Reason', validators=[Optional(), Length(max=255)])

class AddVisitForm(FlaskForm):
    visit_date = DateField('Visit Date', default=date.today, validators=[DataRequired()])
    reason_code = SelectField("Reason Code", choices=[], validators=[Optional()])
    diagnosis_code = StringField("Diagnosis Code", validators=[Optional(), Length(max=256)])
    status = SelectField("Status", choices=[], validators=[DataRequired()])
    class_code = SelectField("Class Code", choices=[], validators=[DataRequired()])
    priority = SelectField("Priority", choices=[], validators=[Optional()])
    location = SelectField("Location", choices=[], validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Add Visit')
