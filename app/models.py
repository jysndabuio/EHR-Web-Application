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
    appointments = relationship('Appointment', back_populates='patient', lazy='select')
    visits = relationship('Visit', back_populates='patient')

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
    visit_date = db.Column(db.DateTime, nullable=False)  # Date and time of the visit
    reason_code = db.Column(db.String(256), nullable=True)  # Reason for the visit (FHIR codeable concept)
    diagnosis_code = db.Column(db.String(256), nullable=True)  # Diagnosis code (if applicable)
    status = db.Column(db.String(64), nullable=False, default="planned")  # e.g., planned, completed
    location = db.Column(db.String(256), nullable=True)  # Location of the visit
    notes = db.Column(db.Text, nullable=True)  # Additional notes

    # Relationships
    patient = relationship('Patient', back_populates='visits')
    doctor = relationship('User', back_populates='visits')
    observations = relationship('Observation', back_populates='visit', foreign_keys='Observation.visit_id')
    procedures = relationship('Procedure', back_populates='visit', foreign_keys='Procedure.visit_id')
    medications = relationship('MedicationStatement', back_populates='visit',foreign_keys='MedicationStatement.visit_id')
    immunizations = relationship('Immunization', back_populates='visit', foreign_keys='Immunization.visit_id')
    vitals = relationship('Vitals', back_populates='visit',  foreign_keys='Vitals.visit_id')
    allergies = relationship('AllergyIntolerance', back_populates='visit',  foreign_keys='AllergyIntolerance.visit_id')
    medical_histories = relationship('MedicalHistory', back_populates='visit',foreign_keys='MedicalHistory.visit_id')
    appointments = relationship('Appointment', back_populates='visit', foreign_keys='Appointment.visit_id')

    def __repr__(self):
        return f'<Visit {self.id} for Patient {self.patient_id}>'

    def to_dict(self):
        """Convert the Visit object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "visit_date": self.visit_date.isoformat() if self.visit_date else None,
            "reason_code": self.reason_code,
            "diagnosis_code": self.diagnosis_code,
            "status": self.status,
            "location": self.location,
            "notes": self.notes
        }

    @staticmethod
    def get_reason_codes():
        """Retrieve predefined reason codes."""
        return [
            {"code": "185349003", "display": "Routine health check"},
            {"code": "386661006", "display": "Fever"},
            {"code": "162864005", "display": "Cough"},
            {"code": "84229001", "display": "Headache"},
            {"code": "422587007", "display": "Follow-up examination"},
            {"code": "281647001", "display": "Postoperative follow-up"},
            {"code": "183460006", "display": "Diabetes management"},
            {"code": "308335008", "display": "Hypertension monitoring"},
            {"code": "225323000", "display": "Preventive care"},
            {"code": "409586006", "display": "Immunization"},
            {"code": "161832001", "display": "Physical therapy visit"},
            {"code": "168537006", "display": "Chest pain"},
            {"code": "182888003", "display": "Injury follow-up"}
        ]

    @staticmethod
    def get_status_codes():
        """Retrieve predefined status codes."""
        return [
            {"code": "planned", "display": "Planned"},
            {"code": "in-progress", "display": "In Progress"},
            {"code": "completed", "display": "Completed"},
            {"code": "cancelled", "display": "Cancelled"}
        ]

class Observation(UserMixin,db.Model):
    __tablename__ = 'observation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    #effectiveDateTime = db.Column(db.Date, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='observations')
    visit = relationship('Visit', back_populates='observations', foreign_keys=[visit_id])

class AllergyIntolerance(UserMixin,db.Model):
    __tablename__ = 'allergy_intolerance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    substance = db.Column(db.String(100), nullable=False)
    clinical_status = db.Column(db.String(20), nullable=True)
    verification_status = db.Column(db.String(20), nullable=True)
    severity = db.Column(db.String(20), nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='allergies')
    visit = relationship('Visit', back_populates='allergies', foreign_keys=[visit_id])

# Medication Model (FHIR: MedicationStatement)
class MedicationStatement(UserMixin,db.Model):
    __tablename__ = 'medication_statement'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    medication = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    effectivePeriod_start = db.Column(db.Date, nullable=True)
    effectivePeriod_end = db.Column(db.Date, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='medications')
    visit = relationship('Visit', back_populates='medications', foreign_keys=[visit_id])

    
# Appointment Model (FHIR: Appointment)
class Appointment(UserMixin,db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=True)  # Set nullable=True if an appointment can exist without a visit
    doctor_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    reason = db.Column(db.String(255), nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('User', back_populates='appointments')
    visit = relationship('Visit', back_populates='appointments', foreign_keys=[visit_id])


# Immunization Model (FHIR: Immunization)
class Immunization(UserMixin,db.Model):
    __tablename__ = 'immunization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    vaccine_code = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)
    lot_number = db.Column(db.String(50), nullable=True)
    site = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='immunizations')
    visit = relationship('Visit', back_populates='immunizations', foreign_keys=[visit_id])

# Procedure Model (FHIR: Procedure)
class Procedure(UserMixin,db.Model):
    __tablename__ = 'procedure'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=True)
    performed_date = db.Column(db.Date, nullable=True)
    performer_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='procedures')
    performer = relationship('User', back_populates='procedures')
    visit = relationship('Visit', back_populates='procedures', foreign_keys=[visit_id])


# Vitals Model (FHIR: Observation for Vitals)
class Vitals(UserMixin,db.Model):
    __tablename__ = 'vitals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    date_recorded = db.Column(db.DateTime, nullable=False)

    # Relationships
    patient = relationship('Patient', back_populates='vitals')
    visit = relationship('Visit', back_populates='vitals', foreign_keys=[visit_id])

    
# Medical History Model (Custom: History)
class MedicalHistory(UserMixin,db.Model):
    __tablename__ = 'medical_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    onset_date = db.Column(db.Date, nullable=True)
    resolution_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='medical_history')
    visit = relationship('Visit', back_populates='medical_histories', foreign_keys=[visit_id])
