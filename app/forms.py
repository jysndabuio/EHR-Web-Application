# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField,FormField,FileField, FieldList,DateTimeField,TextAreaField, DateField, PasswordField, SelectField, TelField, SubmitField, HiddenField, EmailField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange, Optional, ValidationError
from datetime import date, datetime
from .models import MedicationStatement, Observation, AllergyIntolerance, Vitals, Procedure,Appointment, MedicalHistory, Immunization, User, Visit
from flask_wtf.file import FileAllowed, FileRequired

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
        self.category.choices = [(adherence['code'], adherence['display']) for adherence in MedicationStatement.get_category_codes()]

class VisitForm(FlaskForm):
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    doctor_id = HiddenField('Doctor ID', validators=[DataRequired()])
    visit_date = DateTimeField('Visit Date', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    visit_type = StringField('Visit Type', validators=[Optional(), Length(max=50)])
    medications = FieldList(FormField(MedicationStatementForm), min_entries=1, max_entries=10)
    notes = TextAreaField('Notes', validators=[Optional()])

class ObservationForm(FlaskForm):
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    code = SelectField('Observation Code', choices=[], validators=[DataRequired(), Length(max=100)])  # LOINC or SNOMED code
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
        self.category.choices = [(category['code'], category['display']) for category in Observation.get_category_options()]
        
        # Dynamically populate choices for code
        self.code.choices = [(code['code'], code['display']) for code in Observation.get_code_options()]

class ProcedureForm(FlaskForm):
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[], validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    code = StringField('Procedure Code')
    performed_date = DateField('Performed Date')
    reason_code = StringField('Reason Code')
    outcome = SelectField('Outcome', choices=[], validators=[DataRequired()])
    report = TextAreaField('Report')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ProcedureForm, self).__init__(*args, **kwargs)
        self.status.choices = [(
            status['code'], status['display']) for status in Procedure.get_status_options()]
        self.category.choices = [(
            category['code'], category['display']) for category in Procedure.get_category_options()]
        self.outcome.choices = [(
            outcome['code'], outcome['display']) for outcome in Procedure.get_outcome_options()]

class VitalsForm(FlaskForm):
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[], validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    code = StringField('Code')
    effective_date = DateTimeField('Effective Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    value = StringField('Value')
    unit = SelectField('Unit', choices=[], validators=[DataRequired()])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(VitalsForm, self).__init__(*args, **kwargs)
        self.status.choices = [(status['code'], status['display']) for status in Vitals.get_status_options()]
        self.category.choices = [(category['code'], category['display']) for category in Vitals.get_category_options()]
        self.unit.choices = [(unit['code'], unit['display']) for unit in Vitals.get_unit_options()]
        self.code.choices = [(code['code'], code['display']) for code in Vitals.get_code_options()]

class AllergyIntoleranceForm(FlaskForm):
    # Hidden fields for patient and visit IDs
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    
    # Main fields from the model
    substance = StringField('Substance', validators=[DataRequired(), Length(max=100)])  # Substance field
    clinical_status = SelectField('Clinical Status', validators=[Optional()])  # Clinical status dropdown
    verification_status = SelectField('Verification Status', validators=[Optional()])  # Verification status dropdown
    severity = SelectField('Severity', validators=[Optional()])  # Severity dropdown
    type = StringField('Type', validators=[Optional(), Length(max=20)])  # Type field (optional)
    category = SelectField('Category', validators=[Optional()])  # Category dropdown
    reaction = TextAreaField('Reaction', validators=[Optional()])  # Reaction text field
    onset = SelectField('Onset', validators=[Optional()])  # Onset dropdown with Immediate/Delayed choices

    # Dynamically populate choices for select fields in the constructor
    def __init__(self, *args, **kwargs):
        super(AllergyIntoleranceForm, self).__init__(*args, **kwargs)
        
        # Dynamically load the choices for clinical_status, verification_status, severity, and category
        self.clinical_status.choices = [(status['code'], status['display']) for status in AllergyIntolerance.get_clinical_status_codes()]
        self.verification_status.choices = [(status['code'], status['display']) for status in AllergyIntolerance.get_verification_status_codes()]
        self.severity.choices = [(severity['code'], severity['display']) for severity in AllergyIntolerance.get_severity_levels()]
        self.category.choices = [(category['code'], category['display']) for category in AllergyIntolerance.get_category_options()]
        self.onset.choices = [(onset['code'], onset['display']) for onset in AllergyIntolerance.get_onset_choices()]

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

    # Dynamically set the choices for the fields in the form constructor
    def __init__(self, *args, **kwargs):
        super(ImmunizationForm, self).__init__(*args, **kwargs)
        
        self.vaccine_code.choices = [(item["code"], item["display"]) for item in Immunization.get_vaccine_codes()]
        self.status.choices = [(item["code"], item["display"]) for item in Immunization.get_status_codes()]
        self.site.choices = [(item["code"], item["display"]) for item in Immunization.get_site_options()]
        self.route.choices = [(item["code"], item["display"]) for item in Immunization.get_route_options()]

class MedicalHistoryForm(FlaskForm):
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    visit_id = HiddenField('Visit ID', validators=[DataRequired()])
    clinical_status = SelectField('Clinical Status', choices=[], validators=[DataRequired()])
    verification_status = SelectField('Verification Status', choices=[], validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    code = StringField('Condition Code')
    onset_date = DateField('Onset Date', validators=[DataRequired()])
    abatement_date = DateField('Abatement Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(MedicalHistoryForm, self).__init__(*args, **kwargs)
        self.clinical_status.choices = [(
            status['code'], status['display']) for status in MedicalHistory.get_clinical_status_options()]
        self.verification_status.choices = [(
            status['code'], status['display']) for status in MedicalHistory.get_verification_status_options()]
        self.category.choices = [(
            category['code'], category['display']) for category in MedicalHistory.get_category_options()]
        self.code.choices = [(
            category['code'], category['display']) for category in MedicalHistory.get_code_options()]

class AppointmentForm(FlaskForm):
    id = HiddenField('Appointment ID', validators=[Optional()])
    patient_id = HiddenField('Patient ID', validators=[DataRequired()])
    doctor_id = HiddenField('Doctor ID', validators=[DataRequired()])
    visit_id = HiddenField('Visit ID', validators=[Optional()])
    status = SelectField('Status', choices=[], validators=[DataRequired()])
    service_category = SelectField('Service Category', choices=[], validators=[Optional(), Length(max=100)])
    service_type = SelectField('Service Type', choices=[], validators=[Optional(), Length(max=100)])
    specialty = SelectField('Specialty', choices=[], validators=[Optional(), Length(max=100)])
    appointment_type = SelectField('Appointment Type', choices=[], validators=[Optional()])
    reason_code = SelectField('Reason Code', choices=[],  validators=[Optional(), Length(max=255)])
    priority = SelectField('Priority', choices=[], validators=[Optional()])
    start = DateTimeField('Start Date and Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    end = DateTimeField('End Date and Time', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    participant_actor = SelectField('Participant Actor', choices=[], validators=[Optional(), Length(max=50)])
    participant_status = SelectField('Participant Status', choices=[], validators=[Optional(), Length(max=20)])

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)

        # Dynamically populate choices for status
        self.status.choices = [(status['code'], status['display']) for status in Appointment.get_status_options()]

        # Dynamically populate choices for appointment type
        self.appointment_type.choices = [(atype['code'], atype['display']) for atype in Appointment.get_appointment_types()]

        # Dynamically populate choices for priority
        self.priority.choices = [(priority['code'], priority['display']) for priority in Appointment.get_priority_options()]
        # Dynamically populate choices for service category
        self.service_category.choices = [(category['code'], category['display']) for category in Appointment.get_service_categories()]

        # Dynamically populate choices for service type
        self.service_type.choices = [(service['code'], service['display']) for service in Appointment.get_service_types()]

        # Dynamically populate choices for specialty
        self.specialty.choices = [(specialty['code'], specialty['display']) for specialty in Appointment.get_specialties()]

        # Dynamically populate choices for participant actor
        self.participant_actor.choices = [(actor['code'], actor['display']) for actor in Appointment.get_participant_actors()]

        # Dynamically populate choices for participant status
        self.participant_status.choices = [(status['code'], status['display']) for status in Appointment.get_participant_statuses()]

        self.reason_code.choices = [(status['code'], status['display']) for status in Appointment.get_reason_codes()]

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

    # Dynamically set the choices for the fields in the form constructor
    def __init__(self, *args, **kwargs):
        super(AddVisitForm, self).__init__(*args, **kwargs)

        # Populate dynamic fields using model methods
        self.reason_code.choices = [(item["code"], item["display"]) for item in Visit.get_reason_codes()]
        self.status.choices = [(item["code"], item["display"]) for item in Visit.get_status_codes()]
        self.class_code.choices = [(item["code"], item["display"]) for item in Visit.get_class_codes()]
        self.priority.choices = [(item["code"], item["display"]) for item in Visit.get_priority_codes()]
        self.location.choices = [(item["code"], item["display"]) for item in Visit.get_locations()]
        
class SurveyForm(FlaskForm):
    q1 = RadioField('I think that I would like to use this system frequently.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q2 = RadioField('I found the system unnecessarily complex.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q3 = RadioField('I thought the system was easy to use.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q4 = RadioField('I think that I would need the support of a technical person to be able to use this system.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q5 = RadioField('I found the various functions in this system were well integrated.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q6 = RadioField('I thought there was too much inconsistency in this system.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q7 = RadioField('I would imagine that most people would learn to use this system very quickly.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q8 = RadioField('I found the system very cumbersome to use.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q9 = RadioField('I felt very confident using the system.',
                    choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                             ('4', 'Agree'), ('5', 'Strongly Agree')])
    q10 = RadioField('I needed to learn a lot of things before I could get going with this system.',
                     choices=[('1', 'Strongly Disagree'), ('2', 'Disagree'), ('3', 'Neutral'), 
                              ('4', 'Agree'), ('5', 'Strongly Agree')])
    submit = SubmitField("Submit Survey")

class UploadDocumentForm(FlaskForm):
    document_name = StringField('Document Name', validators=[DataRequired()])
    document_file = FileField('Select File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, and DOCX files are allowed!')
    ])

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')