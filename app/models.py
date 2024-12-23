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
    #cascade='all, delete-orphan' will delete all child information link to this patient
    doctor_relationships = relationship('DoctorPatient', back_populates='patient', cascade='all, delete-orphan', lazy='dynamic')
    immunizations = relationship('Immunization', back_populates='patient', cascade='all, delete-orphan',  lazy='select')
    procedures = relationship('Procedure', back_populates='patient', cascade='all, delete-orphan', lazy='select')
    vitals = relationship('Vitals', back_populates='patient',cascade='all, delete-orphan', lazy='select')
    medical_history = relationship('MedicalHistory', back_populates='patient', cascade='all, delete-orphan', lazy='select')
    allergies = relationship('AllergyIntolerance', back_populates='patient', cascade='all, delete-orphan', lazy='select')
    observations = relationship('Observation', back_populates='patient', cascade='all, delete-orphan',  lazy='select')
    medications = relationship('MedicationStatement', back_populates='patient', cascade='all, delete-orphan', lazy='select')
    appointments = relationship('Appointment', back_populates='patient',cascade='all, delete-orphan',  lazy='select')
    visits = relationship('Visit', back_populates='patient')

    @staticmethod
    def generate_patient_id(session):
        """
        Generates a unique patient ID in the format MDHS-2024-XXXX.
        """
        current_year = datetime.now().year
        prefix = f"MDHS-{current_year}-"

        # Query the last patient_id for the current year, ordering by ID
        last_patient = (
            session.query(Patient)
            .filter(Patient.patient_id.like(f"{prefix}%"))
            .order_by(Patient.patient_id.desc())
            .first()
        )

        if last_patient and last_patient.patient_id:
            # Extract the numeric part and increment it
            last_number = int(last_patient.patient_id.split('-')[-1])
            new_number = last_number + 1
        else:
            # Start from 1 if no patient exists
            new_number = 1

        # Format the patient ID with zero-padded suffix
        return f"{prefix}{str(new_number).zfill(4)}"


@event.listens_for(Patient, 'before_insert')
def set_patient_id(mapper, connection, target):
    if not target.patient_id:
        # Use a scoped session to lock and ensure thread safety
        session = db.session

        with session.begin_nested():
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
    status = db.Column(db.String(64), nullable=False, default="planned")  # e.g., planned, in-progress, completed
    class_code = db.Column(db.String(64), nullable=True, default="outpatient")  # Class: outpatient, inpatient, virtual
    priority = db.Column(db.String(20), nullable=True)  # Priority: routine, urgent, stat
    location = db.Column(db.String(256), nullable=True)  # Location of the visit
    notes = db.Column(db.Text, nullable=True)  # Additional notes

    # Relationships
    patient = relationship('Patient', back_populates='visits')
    doctor = relationship('User', back_populates='visits')
    observations = relationship('Observation', back_populates='visit', cascade='all, delete-orphan', foreign_keys='Observation.visit_id')
    procedures = relationship('Procedure', back_populates='visit', cascade='all, delete-orphan', foreign_keys='Procedure.visit_id')
    medications = relationship('MedicationStatement', back_populates='visit', cascade='all, delete-orphan', foreign_keys='MedicationStatement.visit_id')
    immunizations = relationship('Immunization', back_populates='visit', cascade='all, delete-orphan', foreign_keys='Immunization.visit_id')
    vitals = relationship('Vitals', back_populates='visit', cascade='all, delete-orphan', foreign_keys='Vitals.visit_id')
    allergies = relationship('AllergyIntolerance', back_populates='visit', cascade='all, delete-orphan', foreign_keys='AllergyIntolerance.visit_id')
    medical_histories = relationship('MedicalHistory', back_populates='visit', cascade='all, delete-orphan', foreign_keys='MedicalHistory.visit_id')
    appointments = relationship('Appointment', back_populates='visit', cascade='all, delete-orphan', foreign_keys='Appointment.visit_id')

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
            "class_code": self.class_code,
            "priority": self.priority,
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

    @property
    def reason_code_description(self):
        """Compute the reason code description dynamically."""
        reason_code_map = {item["code"]: item["display"] for item in Visit.get_reason_codes()}
        return reason_code_map.get(self.reason_code, "Unknown Reason")
    
    @staticmethod
    def get_status_codes():
        """Retrieve predefined status codes."""
        return [
            {"code": "planned", "display": "Planned"},
            {"code": "in-progress", "display": "In Progress"},
            {"code": "completed", "display": "Completed"},
            {"code": "cancelled", "display": "Cancelled"}
        ]

    @staticmethod
    def get_class_codes():
        """Retrieve predefined class codes."""
        return [
            {"code": "outpatient", "display": "Outpatient"},
            {"code": "inpatient", "display": "Inpatient"},
            {"code": "virtual", "display": "Virtual"}
        ]

    @staticmethod
    def get_priority_codes():
        """Retrieve predefined priority codes."""
        return [
            {"code": "routine", "display": "Routine"},
            {"code": "urgent", "display": "Urgent"},
            {"code": "stat", "display": "Stat"}
        ]
    
    @staticmethod
    def get_locations():
        """Retrieve predefined locations."""
        return [
            {"code": "clinic_a", "display": "Clinic A"},
            {"code": "clinic_b", "display": "Clinic B"},
            {"code": "virtual", "display": "Virtual"},
            {"code": "hospital_room_101", "display": "Hospital Room 101"}
        ]

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Observation(UserMixin, db.Model):
    __tablename__ = 'observation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    code = db.Column(db.String(100), nullable=False)  # This is a LOINC or SNOMED code
    value = db.Column(db.String(50), nullable=True)  # The value of the observation (e.g., 37.0, "Normal")
    status = db.Column(db.String(20), nullable=True)  # Observation status (e.g., "final", "preliminary")
    category = db.Column(db.String(50), nullable=True)  # Category for the observation (e.g., "vital-signs")
    effectiveDateTime = db.Column(db.DateTime, nullable=True)  # Effective date/time

    # Relationships
    patient = relationship('Patient', back_populates='observations')
    visit = relationship('Visit', back_populates='observations', foreign_keys=[visit_id])

    # Additional relationships for dynamic loading options
    # If you want to create tables for status, category, and code options
    # Example (assuming tables `ObservationStatus`, `ObservationCategory`, and `ObservationCode`)
    # status_ref = db.Column(db.Integer, db.ForeignKey('observation_status.id'), nullable=True)
    # category_ref = db.Column(db.Integer, db.ForeignKey('observation_category.id'), nullable=True)
    # code_ref = db.Column(db.Integer, db.ForeignKey('observation_code.id'), nullable=True)

    @staticmethod
    def get_status_options():
        """Returns a list of possible status options."""
        return [
            {"code": "registered", "display": "Registered"},
            {"code": "preliminary", "display": "Preliminary"},
            {"code": "final", "display": "Final"},
            {"code": "amended", "display": "Amended"},
            {"code": "cancelled", "display": "Cancelled"}
        ]

    @staticmethod
    def get_category_options():
        """Returns a list of possible category options."""
        return [
            {"code": "vital-signs", "display": "Vital Signs"},
            {"code": "laboratory", "display": "Laboratory"},
            {"code": "imaging", "display": "Imaging"}
        ]

    @staticmethod
    def get_code_options():
        """Returns a list of possible code options (e.g., LOINC or SNOMED codes) for observations."""
        return [
            # Laboratory Tests
            {"code": "4548-4", "display": "Hemoglobin A1c (HbA1c)"},
            {"code": "718-7", "display": "Hemoglobin"},
            {"code": "6690-2", "display": "White Blood Cell Count"},
            {"code": "789-8", "display": "Erythrocyte Sedimentation Rate (ESR)"},
            {"code": "2345-7", "display": "Glucose, Blood"},
            {"code": "6299-2", "display": "Cholesterol, Total"},
            {"code": "2093-3", "display": "Low-Density Lipoprotein (LDL)"},
            {"code": "2571-8", "display": "High-Density Lipoprotein (HDL)"},
            {"code": "32354-0", "display": "Urea Nitrogen (BUN)"},
            {"code": "2823-3", "display": "Potassium, Blood"},
            {"code": "2710-2", "display": "Sodium, Blood"},
            {"code": "2160-0", "display": "Creatinine, Blood"},
            {"code": "2339-0", "display": "Glucose, Urine"},

            # Imaging and Diagnostic Reports
            {"code": "24627-2", "display": "Chest X-ray Report"},
            {"code": "18748-4", "display": "CT Head Report"},
            {"code": "72273-1", "display": "MRI Abdomen Report"},
            {"code": "11502-2", "display": "Mammogram Report"},
            {"code": "30746-8", "display": "Ultrasound Pelvis Report"},

            # Infectious Disease and Microbiology
            {"code": "94500-6", "display": "COVID-19 PCR Test"},
            {"code": "22322-2", "display": "HIV Antibody Test"},
            {"code": "20570-8", "display": "Hepatitis B Surface Antigen"},
            {"code": "58413-6", "display": "Influenza Virus A RNA"},
            {"code": "24111-1", "display": "Streptococcus Test"},

            # Cancer Markers
            {"code": "10834-0", "display": "Prostate-Specific Antigen (PSA)"},
            {"code": "19295-5", "display": "CA-125 (Cancer Antigen 125)"},
            {"code": "19825-1", "display": "Alpha-Fetoprotein (AFP)"},
            {"code": "2101-1", "display": "Carcinoembryonic Antigen (CEA)"},

            # Pregnancy and Fertility
            {"code": "19080-1", "display": "Pregnancy Test"},
            {"code": "14743-9", "display": "Gestational Age"},
            {"code": "32458-4", "display": "Human Chorionic Gonadotropin (hCG), Serum"},
            {"code": "34682-5", "display": "Progesterone, Serum"},

            # Other Clinical Observations
            {"code": "15074-8", "display": "Oxygen Saturation (SpO2)"},
            {"code": "9278-3", "display": "Pain Score"},
            {"code": "24841-1", "display": "Alcohol Level, Blood"},
            {"code": "49541-6", "display": "Drug Screen, Urine"},
            {"code": "40545-1", "display": "Mood Assessment"},
            {"code": "75323-6", "display": "Cognitive Function Assessment"}
        ]
    
    @property
    def code_description(self):
        """Compute the code description dynamically."""
        code_map = {item["code"]: item["display"] for item in Observation.get_code_options()}
        return code_map.get(self.code, "Unknown Reason")


# Updated AllergyIntolerance Model
class AllergyIntolerance(UserMixin, db.Model):
    __tablename__ = 'allergy_intolerance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    substance = db.Column(db.String(100), nullable=False)  # This can be extended to reference a code system
    clinical_status = db.Column(db.String(20), nullable=True)
    verification_status = db.Column(db.String(20), nullable=True)
    severity = db.Column(db.String(20), nullable=True)
    type = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    reaction = db.Column(db.Text, nullable=True)
    onset = db.Column(db.String(20), nullable=True)  # This field will store 'immediate' or 'delayed'


    # Relationships
    patient = relationship('Patient', back_populates='allergies')
    visit = relationship('Visit', back_populates='allergies', foreign_keys=[visit_id])

    @staticmethod
    def get_clinical_status_codes():
        return [
            {"code": "active", "display": "Active"},
            {"code": "inactive", "display": "Inactive"},
            {"code": "resolved", "display": "Resolved"}
        ]

    @staticmethod
    def get_verification_status_codes():
        return [
            {"code": "confirmed", "display": "Confirmed"},
            {"code": "unconfirmed", "display": "Unconfirmed"},
            {"code": "refuted", "display": "Refuted"}
        ]

    @staticmethod
    def get_severity_levels():
        return [
            {"code": "mild", "display": "Mild"},
            {"code": "moderate", "display": "Moderate"},
            {"code": "severe", "display": "Severe"}
        ]

    @staticmethod
    def get_category_options():
        """Retrieve predefined category codes for the allergy (e.g., food, medication)."""
        return [
            {"code": "food", "display": "Food"},
            {"code": "medication", "display": "Medication"},
            {"code": "environmental", "display": "Environmental"}
        ]
    
    @staticmethod
    def get_onset_choices():
        """Retrieve predefined onset choices for allergic reactions (immediate or delayed)."""
        return [
            {"code": "immediate", "display": "Immediate"},
            {"code": "delayed", "display": "Delayed"}
        ]

# Updated MedicationStatement Model
class MedicationStatement(UserMixin, db.Model):
    __tablename__ = 'medication_statement'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    medication_code = db.Column(db.String(100), nullable=False)  # Consider referencing a code system (e.g., RxNorm)
    medication_name = db.Column(db.String(300), nullable=False)  # Name or description of the medication
    status = db.Column(db.String(20), nullable=False)  # e.g., "active", "completed"
    effectivePeriod_start = db.Column(db.Date, nullable=True)
    effectivePeriod_end = db.Column(db.Date, nullable=True)
    date_asserted = db.Column(db.Date, nullable=True)  # When the statement was recorded
    information_source = db.Column(db.String(255), nullable=True)  # Who reported the medication (e.g., doctor, patient)
    adherence = db.Column(db.String(20), nullable=True)  # Compliant status
    reason_code = db.Column(db.Text, nullable=True)  # Reason for medication (e.g., "Hypertension")
    reason_reference = db.Column(db.String(100), nullable=True)  # Reference to related condition or observation
    status_reason = db.Column(db.String(255), nullable=True)  # Reason for status change
    dosage_instruction = db.Column(db.Text, nullable=True)  # Detailed dosage instructions
    notes = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(64), nullable=True, default="outpatient")  # Class: outpatient, inpatient, virtual
    route_of_administration = db.Column(db.String(100), nullable=True)  # Route (e.g., "oral", "IV")
    timing = db.Column(db.String(100), nullable=True)  # Timing of dosage (e.g., "twice daily")

    # Relationships
    patient = relationship('Patient', back_populates='medications')
    visit = relationship('Visit', back_populates='medications', foreign_keys=[visit_id])

    @staticmethod
    def get_status_codes():
        return [
            {"code": "active", "display": "Active"},
            {"code": "completed", "display": "Completed"},
            {"code": "entered-in-error", "display": "Entered in Error"},
            {"code": "intended", "display": "Intended"},
            {"code": "stopped", "display": "Stopped"},
            {"code": "on-hold", "display": "On Hold"}
        ]

    @staticmethod
    def get_adherence_codes():
        """Retrieve predefined adherence options (e.g., compliant, non-compliant)."""
        return [
            {"code": "compliant", "display": "Compliant"},
            {"code": "non-compliant", "display": "Non-compliant"},
            {"code": "unknown", "display": "Unknown"}
        ]

    @staticmethod
    def get_category_codes():
        """Retrieve predefined categories (e.g., inpatient, outpatient)."""
        return [
            {"code": "outpatient", "display": "Outpatient"},
            {"code": "inpatient", "display": "Inpatient"},
            {"code": "virtual", "display": "Virtual"}
        ]

# Updated Immunization Model with more vaccines
class Immunization(UserMixin, db.Model):
    __tablename__ = 'immunization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    vaccine_code = db.Column(db.String(100), nullable=False)  # This can be extended to reference a code system (e.g., SNOMED)
    status = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)
    lot_number = db.Column(db.String(50), nullable=True)
    site = db.Column(db.String(50), nullable=True)
    route = db.Column(db.String(50), nullable=True)
    dose_quantity = db.Column(db.String(20), nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)  # Add manufacturer details
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='immunizations')
    visit = relationship('Visit', back_populates='immunizations', foreign_keys=[visit_id])

    @staticmethod
    def get_status_codes():
        return [
            {"code": "completed", "display": "Completed"},
            {"code": "entered-in-error", "display": "Entered in Error"},
            {"code": "not-done", "display": "Not Done"}
        ]

    @staticmethod
    def get_site_options():
        return [
            {"code": "left-arm", "display": "Left Arm"},
            {"code": "right-arm", "display": "Right Arm"},
            {"code": "left-thigh", "display": "Left Thigh"},
            {"code": "right-thigh", "display": "Right Thigh"}
        ]

    @staticmethod
    def get_route_options():
        return [
            {"code": "IM", "display": "Intramuscular"},
            {"code": "SC", "display": "Subcutaneous"},
            {"code": "ID", "display": "Intradermal"}
        ]

    @staticmethod
    def get_vaccine_codes():
        """Retrieve predefined vaccine codes or list."""
        return [
            {"code": "207", "display": "Influenza, Inactivated"},
            {"code": "141", "display": "Measles, Mumps, Rubella (MMR)"},
            {"code": "152", "display": "COVID-19"},
            {"code": "151", "display": "Hepatitis A"},
            {"code": "150", "display": "Hepatitis B"},
            {"code": "33", "display": "Polio, Inactivated (IPV)"},
            {"code": "21", "display": "Diphtheria, Tetanus, Pertussis (DTaP)"},
            {"code": "74", "display": "Tetanus, Diphtheria (TD)"},
            {"code": "136", "display": "Varicella (Chickenpox)"},
            {"code": "126", "display": "Pneumococcal conjugate (PCV13)"},
            {"code": "133", "display": "Pneumococcal polysaccharide (PPSV23)"},
            {"code": "127", "display": "Haemophilus influenzae type b (Hib)"},
            {"code": "88", "display": "Meningococcal conjugate (MCV4)"},
            {"code": "49", "display": "Human Papillomavirus (HPV)"},
            {"code": "132", "display": "Rotavirus"},
            {"code": "172", "display": "Zoster (Shingles)"},
            {"code": "97", "display": "Typhoid"},
            {"code": "56", "display": "Yellow Fever"},
            {"code": "67", "display": "Rabies"},
            {"code": "104", "display": "Japanese Encephalitis"},
            {"code": "80", "display": "Cholera"}
        ]

    @property
    def vaccine_code_description(self):
        """Compute the vaccine code description dynamically."""
        vaccine_code_map = {item["code"]: item["display"] for item in Immunization.get_vaccine_codes()}
        return vaccine_code_map.get(self.vaccine_code, "Unknown Reason")
    
class Appointment(UserMixin, db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=True)
    doctor_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # e.g., booked, cancelled, noshow
    service_category = db.Column(db.String(100), nullable=True)  # e.g., General Practice, Cardiology
    service_type = db.Column(db.String(100), nullable=True)  # e.g., Consultation, Immunization
    specialty = db.Column(db.String(100), nullable=True)  # e.g., Pediatrics, Orthopedics
    appointment_type = db.Column(db.String(50), nullable=True)  # e.g., routine, urgent
    reason_code = db.Column(db.String(255), nullable=True)  # Reason for appointment
    priority = db.Column(db.String(50), nullable=True)  # e.g., routine, urgent
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=True)
    participant_actor = db.Column(db.String(50), nullable=True)  # Actor (e.g., patient, practitioner)
    participant_status = db.Column(db.String(20), nullable=True)  # e.g., accepted, declined, tentative

    # Relationships
    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('User', back_populates='appointments')
    visit = relationship('Visit', back_populates='appointments', foreign_keys=[visit_id])

    @staticmethod
    def get_status_options():
        return [
            {"code": "proposed", "display": "Proposed"},
            {"code": "pending", "display": "Pending"},
            {"code": "booked", "display": "Booked"},
            {"code": "arrived", "display": "Arrived"},
            {"code": "fulfilled", "display": "Fulfilled"},
            {"code": "cancelled", "display": "Cancelled"},
            {"code": "noshow", "display": "No Show"},
            {"code": "entered-in-error", "display": "Entered in Error"},
            {"code": "checked-in", "display": "Checked In"},
            {"code": "waitlist", "display": "Waitlist"}
        ]
    
    @staticmethod
    def get_service_types():
        return [
            {"code": "consultation", "display": "Consultation"},
            {"code": "follow-up", "display": "Follow-Up"},
            {"code": "immunization", "display": "Immunization"},
            {"code": "diagnostic-test", "display": "Diagnostic Test"},
            {"code": "screening", "display": "Screening"},
            {"code": "therapy", "display": "Therapy"},
            {"code": "surgery", "display": "Surgery"}
        ]
    
    @staticmethod
    def get_specialties():
        return [
            {"code": "general-practice", "display": "General Practice"},
            {"code": "cardiology", "display": "Cardiology"},
            {"code": "dermatology", "display": "Dermatology"},
            {"code": "orthopedics", "display": "Orthopedics"},
            {"code": "pediatrics", "display": "Pediatrics"},
            {"code": "psychiatry", "display": "Psychiatry"},
            {"code": "gynecology", "display": "Gynecology"},
            {"code": "urology", "display": "Urology"},
            {"code": "immunology", "display": "Immunology"},
            {"code": "neurology", "display": "Neurology"}
        ]
    

    @staticmethod
    def get_service_categories():
        return [
            {"code": "general-practice", "display": "General Practice"},
            {"code": "cardiology", "display": "Cardiology"},
            {"code": "dermatology", "display": "Dermatology"},
            {"code": "orthopedics", "display": "Orthopedics"},
            {"code": "pediatrics", "display": "Pediatrics"},
            {"code": "psychiatry", "display": "Psychiatry"},
            {"code": "gynecology", "display": "Gynecology"},
            {"code": "urology", "display": "Urology"},
            {"code": "immunology", "display": "Immunology"}
        ]
    
    @staticmethod
    def get_appointment_types():
        return [
            {"code": "routine", "display": "Routine"},
            {"code": "urgent", "display": "Urgent"},
            {"code": "walk-in", "display": "Walk-In"},
            {"code": "emergency", "display": "Emergency"}
        ]

    @staticmethod
    def get_priority_options():
        return [
            {"code": "low", "display": "Low"},
            {"code": "routine", "display": "Routine"},
            {"code": "urgent", "display": "Urgent"},
            {"code": "high", "display": "High"}
        ]

    @staticmethod
    def get_participant_actors():
        return [
            {"code": "patient", "display": "Patient"},
            {"code": "practitioner", "display": "Practitioner"},
            {"code": "related-person", "display": "Related Person"},
            {"code": "organization", "display": "Organization"}
        ]

    @staticmethod
    def get_participant_statuses():
        return [
            {"code": "accepted", "display": "Accepted"},
            {"code": "declined", "display": "Declined"},
            {"code": "tentative", "display": "Tentative"},
            {"code": "needs-action", "display": "Needs Action"}
        ]
    
    @staticmethod
    def get_reason_codes():
        return [
            {"code": "routine", "display": "Routine Check-up"},
            {"code": "urgent", "display": "Urgent Consultation"},
            {"code": "followup", "display": "Follow-up Appointment"},
            {"code": "diagnostic", "display": "Diagnostic Test"},
            {"code": "referral", "display": "Specialist Referral"},
            {"code": "vaccination", "display": "Vaccination"},
            {"code": "emergency", "display": "Emergency"},
            {"code": "chronic", "display": "Chronic Condition Management"},
            {"code": "physical_therapy", "display": "Physical Therapy"},
            {"code": "surgery_consultation", "display": "Consultation for Surgery"},
            {"code": "mental_health", "display": "Mental Health Consultation"},
            {"code": "screening", "display": "Preventive Screening"},
            {"code": "health_maintenance", "display": "Health Maintenance"},
            {"code": "prescription_renewal", "display": "Prescription Renewal"},
            {"code": "preoperative", "display": "Pre-Operative Consultation"}
        ]
class MedicalHistory(UserMixin, db.Model):
    __tablename__ = 'medical_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    clinical_status = db.Column(db.String(50), nullable=True)  # e.g., active, resolved, remission
    verification_status = db.Column(db.String(50), nullable=True)  # e.g., confirmed, provisional
    category = db.Column(db.String(50), nullable=True)  # e.g., problem-list-item, encounter-diagnosis
    code = db.Column(db.String(100), nullable=True)  # Condition code (e.g., SNOMED-CT or ICD-10)
    onset_date = db.Column(db.Date, nullable=True)  # When the condition started
    abatement_date = db.Column(db.Date, nullable=True)  # When the condition ended (if resolved)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    patient = relationship('Patient', back_populates='medical_history')
    visit = relationship('Visit', back_populates='medical_histories', foreign_keys=[visit_id])

    @staticmethod
    def get_clinical_status_options():
        return [
            {"code": "active", "display": "Active"},
            {"code": "resolved", "display": "Resolved"},
            {"code": "remission", "display": "Remission"}
        ]
    
    @staticmethod
    def get_verification_status_options():
        return [
            {"code": "confirmed", "display": "Confirmed"},
            {"code": "provisional", "display": "Provisional"},
            {"code": "differential", "display": "Differential"}
        ]
    
    @staticmethod
    def get_category_options():
        return [
            {"code": "problem-list-item", "display": "Problem List Item"},
            {"code": "encounter-diagnosis", "display": "Encounter Diagnosis"}
        ]


class Procedure(UserMixin, db.Model):
    __tablename__ = 'procedure'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    status = db.Column(db.String(20), nullable=True)  # e.g., completed, not-done, in-progress
    category = db.Column(db.String(50), nullable=True)  # e.g., surgical, diagnostic
    code = db.Column(db.String(100), nullable=True)  # Procedure code (e.g., SNOMED-CT or CPT)
    performed_date = db.Column(db.Date, nullable=True)  # Date of the procedure
    performer_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)
    reason_code = db.Column(db.String(255), nullable=True)  # Reason for the procedure
    outcome = db.Column(db.String(50), nullable=True)  # Outcome of the procedure (e.g., successful)
    report = db.Column(db.Text, nullable=True)  # Reference to diagnostic report

    # Relationships
    patient = relationship('Patient', back_populates='procedures')
    performer = relationship('User', back_populates='procedures')
    visit = relationship('Visit', back_populates='procedures', foreign_keys=[visit_id])

    @staticmethod
    def get_status_options():
        return [
            {"code": "preparation", "display": "Preparation"},
            {"code": "in-progress", "display": "In Progress"},
            {"code": "not-done", "display": "Not Done"},
            {"code": "on-hold", "display": "On Hold"},
            {"code": "stopped", "display": "Stopped"},
            {"code": "completed", "display": "Completed"},
            {"code": "entered-in-error", "display": "Entered in Error"},
            {"code": "unknown", "display": "Unknown"}
        ]
    
    @staticmethod
    def get_category_options():
        return [
            {"code": "surgical", "display": "Surgical"},
            {"code": "diagnostic", "display": "Diagnostic"}
        ]
    
    @staticmethod
    def get_outcome_options():
        return [
            {"code": "successful", "display": "Successful"},
            {"code": "failed", "display": "Failed"},
            {"code": "partial-success", "display": "Partial Success"}
        ]
class Vitals(UserMixin, db.Model):
    __tablename__ = 'vitals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patient_basic.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    status = db.Column(db.String(20), nullable=True)  # e.g., registered, final, amended
    category = db.Column(db.String(50), nullable=True)  # e.g., vital-signs
    code = db.Column(db.String(50), nullable=True)  # Type of observation (e.g., body temperature, blood pressure)
    effective_date = db.Column(db.DateTime, nullable=False)  # Date of observation
    value = db.Column(db.String(50), nullable=True)  # Measured value (e.g., 120/80 for blood pressure)
    unit = db.Column(db.String(20), nullable=True)  # Unit of measurement (e.g., mmHg, °C)

    # Relationships
    patient = relationship('Patient', back_populates='vitals')
    visit = relationship('Visit', back_populates='vitals', foreign_keys=[visit_id])

    @staticmethod
    def get_status_options():
        return [
            {"code": "registered", "display": "Registered"},
            {"code": "preliminary", "display": "Preliminary"},
            {"code": "final", "display": "Final"},
            {"code": "amended", "display": "Amended"},
            {"code": "corrected", "display": "Corrected"},
            {"code": "cancelled", "display": "Cancelled"},
            {"code": "entered-in-error", "display": "Entered in Error"}
        ]
    
    @staticmethod
    def get_category_options():
        return [
            {"code": "vital-signs", "display": "Vital Signs"}
        ]
    
    @staticmethod
    def get_unit_options():
        return [
            {"code": "bpm", "display": "Beats per Minute"},
            {"code": "mmhg", "display": "Millimeters of Mercury"},
            {"code": "celsius", "display": "Celsius (°C)"},
            {"code": "farenheit", "display": "Fahrenheit (°F)"}
        ]

