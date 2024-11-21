import uuid
from datetime import datetime, date
from . import db, bcrypt  # Import db after it's initialized in __init__.py
from flask_login import UserMixin
from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g., MDHS-DOC-2024-0001
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum("admin", "doctor"), nullable=False)  # Role definition
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    id_card_number = db.Column(db.String(15), nullable=False)
    home_address = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=True)
    ecd_name = db.Column(db.String(50), nullable=True)
    ecd_contact_number = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    profile_image = db.Column(db.String(255), nullable=True, default='image/default_profile.jpg')

    # Relationships
    education_records = relationship('UserEducation', back_populates='user', lazy=True)
    patients = relationship('DoctorPatient', back_populates='doctor', lazy='dynamic')
    appointments = relationship('Appointment', back_populates='doctor', lazy='dynamic')
    procedures = relationship('Procedure', back_populates='performer', lazy='dynamic') 
    visits = relationship('Visit', back_populates='doctor', lazy='dynamic')
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password, password)
    

    @staticmethod
    def generate_user_id(session):
        """
        Generates a unique user ID in the format MDHS-USER-2024-XXXX.
        """
        current_year = datetime.now().year
        prefix = f"MDHS-USER-{current_year}-"

        # Get the maximum number suffix used this year
        last_user = session.query(User).filter(
            User.user_id.like(f"{prefix}%")
        ).order_by(User.id.desc()).first()

        if last_user and last_user.user_id:
            # Extract the numeric part and increment it
            last_number = int(last_user.user_id.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        # Format the user ID with zero-padded suffix
        return f"{prefix}{str(new_number).zfill(4)}"


@event.listens_for(User, 'before_insert')
def set_user_id(mapper, connection, target):
    if not target.user_id:
        session = db.session
        target.user_id = User.generate_user_id(session)


class UserEducation(UserMixin, db.Model):
    __tablename__ = 'user_education'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)  # FK to users.id

    med_deg = db.Column(db.String(50), nullable=True)
    med_deg_spec = db.Column(db.String(50), nullable=True)
    board_cert = db.Column(db.String(50), nullable=True)
    license_number = db.Column(db.String(50), nullable=False)
    license_issuer = db.Column(db.String(50), nullable=True)
    license_expiration = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.String(50), nullable=True)

    user = relationship('User', back_populates='education_records', lazy=True)

    def __repr__(self):
        return f'<UserEducation {self.med_deg} for {self.user_id}>'


class Patient(UserMixin, db.Model):
    __tablename__ = 'patient_basic'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g., MDHS-2024-XXXX
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    home_address = db.Column(db.String(100), nullable=False)
    ecd_name = db.Column(db.String(50), nullable=True)
    ecd_contact_number = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationships
    doctor_relationships = relationship('DoctorPatient', back_populates='patient', lazy='dynamic')
    immunizations = relationship('Immunization', back_populates='patient', lazy='dynamic')
    procedures = relationship('Procedure', back_populates='patient', lazy='dynamic')
    vitals = relationship('Vitals', back_populates='patient', lazy='dynamic')
    medical_history = relationship('MedicalHistory', back_populates='patient', lazy='dynamic')
    allergies = relationship('AllergyIntolerance', back_populates='patient', lazy='dynamic')
    observations = relationship('Observation', back_populates='patient', lazy='dynamic')
    medications = relationship('MedicationStatement', back_populates='patient', lazy='dynamic')
    appointments = relationship('Appointment', back_populates='patient', lazy='dynamic')
    visits = relationship('Visit', back_populates='patient', lazy='dynamic')

    @staticmethod
    def generate_patient_id(session):
        """
        Generates a unique patient ID in the format MDHS-2024-XXXX.
        """
        current_year = datetime.now().year
        prefix = f"MDHS-{current_year}-"

        # Get the maximum number suffix used this year
        last_patient = session.query(Patient).filter(
            Patient.patient_id.like(f"{prefix}%")
        ).order_by(Patient.id.desc()).first()

        if last_patient and last_patient.patient_id:
            # Extract the numeric part and increment it
            last_number = int(last_patient.patient_id.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        # Format the patient ID with zero-padded suffix
        return f"{prefix}{str(new_number).zfill(4)}"


@event.listens_for(Patient, 'before_insert')
def set_patient_id(mapper, connection, target):
    if not target.patient_id:
        session = db.session
        target.patient_id = Patient.generate_patient_id(session)

# Updated Many-to-Many Doctor-Patient model
class DoctorPatient(UserMixin, db.Model):
    __tablename__ = 'doctor_patient'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)

    # Relationships
    doctor = relationship('User', back_populates='patients')
    patient = relationship('Patient', back_populates='doctor_relationships')

class Visit(UserMixin, db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    doctor_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=db.func.now())
    visit_type = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='visits')
    doctor = relationship('User', back_populates='visits')
    observations = relationship('Observation', back_populates='visits', lazy='dynamic')
    procedures = relationship('Procedure', back_populates='visits', lazy='dynamic')
    medications = relationship('MedicationStatement', back_populates='visits', lazy='dynamic')
    immunizations = relationship('Immunization', back_populates='visits', lazy='dynamic')
    vitals = relationship('Vitals', back_populates='visits', lazy='dynamic')
    allergies = relationship('AllergyIntolerance', back_populates='visits', lazy='dynamic')
    medical_histories = relationship('MedicalHistory', back_populates='visits', lazy='dynamic')
    appointents = relationship('Visit', back_populates='visits', lazy='dynamic')

    def __repr__(self):
        return f'<Visit {self.id} for Patient {self.patient_id}>'


# Allergy Model (FHIR: AllergyIntolerance)
class AllergyIntolerance(db.Model):
    __tablename__ = 'allergy_intolerance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: AllergyIntolerance.patient
    substance = db.Column(db.String(100), nullable=False)  # FHIR: AllergyIntolerance.substance
    clinical_status = db.Column(db.String(20), nullable=True)  # FHIR: AllergyIntolerance.clinicalStatus
    verification_status = db.Column(db.String(20), nullable=True)  # FHIR: AllergyIntolerance.verificationStatus
    severity = db.Column(db.String(20), nullable=True)  # FHIR: AllergyIntolerance.severity

    # Relationship
    patient = relationship('Patient', back_populates='allergies')
    visits = relationship('Visit', back_populates='allergies', lazy='dynamic')

# Test Model (FHIR: Observation)
class Observation(db.Model):
    __tablename__ = 'observation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: Observation.subject
    code = db.Column(db.String(100), nullable=False)  # FHIR: Observation.code
    value = db.Column(db.String(50), nullable=True)  # FHIR: Observation.valueQuantity
    status = db.Column(db.String(20), nullable=True)  # FHIR: Observation.status
    effectiveDateTime = db.Column(db.DateTime, nullable=True)  # FHIR: Observation.effectiveDateTime

    # Relationship
    patient = relationship('Patient', back_populates='observations')
    visits = relationship('Visit', back_populates='observations', lazy='dynamic')

# Medication Model (FHIR: MedicationStatement)
class MedicationStatement(db.Model):
    __tablename__ = 'medication_statement'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: MedicationStatement.subject
    medication = db.Column(db.String(100), nullable=False)  # FHIR: MedicationStatement.medicationCodeableConcept
    dosage = db.Column(db.String(50), nullable=True)  # FHIR: MedicationStatement.dosage
    status = db.Column(db.String(20), nullable=True)  # FHIR: MedicationStatement.status
    effectivePeriod_start = db.Column(db.Date, nullable=True)  # FHIR: MedicationStatement.effectivePeriod.start
    effectivePeriod_end = db.Column(db.Date, nullable=True)  # FHIR: MedicationStatement.effectivePeriod.end

    # Relationship
    patient = relationship('Patient', back_populates='medications')
    visits = relationship('Visit', back_populates='medications', lazy='dynamic')

# Appointment Model (FHIR: Appointment)
class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: Appointment.participant.patient
    doctor_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)  # FHIR: Appointment.participant.actor
    start = db.Column(db.DateTime, nullable=False)  # FHIR: Appointment.start
    end = db.Column(db.DateTime, nullable=True)  # FHIR: Appointment.end
    status = db.Column(db.String(20), nullable=True)  # FHIR: Appointment.status
    reason = db.Column(db.String(255), nullable=True)  # FHIR: Appointment.reasonCode

    # Relationships
    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('User', back_populates='appointments')
    visits = relationship('Visit', back_populates='appointments', lazy='dynamic')

# Immunization Model (FHIR: Immunization)
class Immunization(db.Model):
    __tablename__ = 'immunization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: Immunization.patient
    vaccine_code = db.Column(db.String(100), nullable=False)  # FHIR: Immunization.vaccineCode
    status = db.Column(db.String(20), nullable=True)  # FHIR: Immunization.status
    date = db.Column(db.Date, nullable=False)  # FHIR: Immunization.occurrenceDateTime
    lot_number = db.Column(db.String(50), nullable=True)  # FHIR: Immunization.lotNumber
    site = db.Column(db.String(50), nullable=True)  # FHIR: Immunization.site
    notes = db.Column(db.Text, nullable=True)  # Custom: Additional notes

    # Relationship
    patient = relationship('Patient', back_populates='immunizations')
    visits = relationship('Visit', back_populates='immunizations', lazy='dynamic')

# Procedure Model (FHIR: Procedure)
class Procedure(db.Model):
    __tablename__ = 'procedure'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: Procedure.subject
    code = db.Column(db.String(100), nullable=False)  # FHIR: Procedure.code
    status = db.Column(db.String(20), nullable=True)  # FHIR: Procedure.status
    performed_date = db.Column(db.Date, nullable=True)  # FHIR: Procedure.performedDateTime
    performer_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)  # FHIR: Procedure.performer
    notes = db.Column(db.Text, nullable=True)  # Custom: Additional notes

    # Relationships
    patient = relationship('Patient', back_populates='procedures')
    performer = relationship('User', back_populates='procedures')
    visits = relationship('Visit', back_populates='procedures', lazy='dynamic')

# Vitals Model (FHIR: Observation for Vitals)
class Vitals(db.Model):
    __tablename__ = 'vitals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)  # FHIR: Observation.subject
    type = db.Column(db.String(50), nullable=False)  # Custom: Vitals type (e.g., Blood Pressure, Heart Rate)
    value = db.Column(db.String(50), nullable=False)  # FHIR: Observation.valueQuantity
    unit = db.Column(db.String(20), nullable=False)  # FHIR: Observation.valueQuantity.unit
    date_recorded = db.Column(db.DateTime, nullable=False)  # FHIR: Observation.effectiveDateTime

    # Relationship
    patient = relationship('Patient', back_populates='vitals')
    visits = relationship('Visit', back_populates='vitals', lazy='dynamic')
    
# Medical History Model (Custom: History)
class MedicalHistory(db.Model):
    __tablename__ = 'medical_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    condition = db.Column(db.String(100), nullable=False)  # E.g., Diabetes, Hypertension
    onset_date = db.Column(db.Date, nullable=True)  # When the condition began
    resolution_date = db.Column(db.Date, nullable=True)  # When the condition was resolved, if applicable
    notes = db.Column(db.Text, nullable=True)  # Additional notes

    # Relationship
    patient = relationship('Patient', back_populates='medical_history')
    visits = relationship('Visit', back_populates='medical_histories', lazy='dynamic')
