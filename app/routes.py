from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime
from .models import User, UserEducation,LabScan, LabScanGroup, AdditionalDocument, DoctorPatient, Patient, Visit, Appointment, SurveyResponse, Vitals, AllergyIntolerance, Observation,Immunization, Procedure,MedicalHistory, MedicationStatement
from .forms import SurveyForm,UploadDocumentForm,RequestResetForm, ResetPasswordForm, RegisterForm,MedicationStatementForm,AllergyIntoleranceForm, AddVisitForm, PatientForm, AppointmentForm, VisitForm, ObservationForm, PasswordResetForm, UserUpdateProfile, PatientUpdateForm, ImmunizationForm, ProcedureForm, VitalsForm, MedicalHistoryForm
from . import db, bcrypt, mail
from .utils import allowed_file, send_reset_email
from .config import Config
from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm import joinedload

bp = Blueprint('main', __name__)

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

@bp.route('/')
def index():
    return render_template('home.html')

@bp.route('/about_me')
@login_required
def about_me():
    return render_template('about_me.html')


@bp.route('/under_construction')
def under_construction():
    return render_template('under_construction.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():

    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect_dashboard(current_user.role)
    

    role = request.args.get('role')
    if not role or role not in ['admin', 'doctor']:
        flash("Invalid role selected. Please select a role.")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, role=role).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect_dashboard(user.role)
        else:
            flash('Invalid username or password.')

    return render_template('login.html', role=role)

#When presented and registration fails.
#No error handling for duplicate username or emails. 
#username and email are unique. 
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    form.role.data = 'doctor'  # Pre-set the role as "doctor"

    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user_by_username = User.query.filter_by(username=form.username.data).first()
        existing_user_by_email = User.query.filter_by(email=form.email.data).first()

        if existing_user_by_username:
            flash('The username is already taken. Please choose a different username.', 'danger')
            return render_template('register.html', form=form)

        if existing_user_by_email:
            flash('The email is already registered. Please use a different email or log in.', 'danger')
            return render_template('register.html', form=form)

        # Create a new User object with role set to "doctor"
        new_user = User(
            username=form.username.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            email=form.email.data,
            role=form.role.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            contact_number=form.contact_number.data,
            age=form.age.data,
            gender=form.gender.data,
            id_card_number=form.id_card_number.data,
            country=form.country.data,
            home_address=form.home_address.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login', role='doctor'))

    return render_template('register.html', form=form)


@bp.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)
    return render_template('patient_dashboard.html', show_return_button=False)

@bp.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)

    return render_template('doctor_dashboard.html')

@bp.route('/patients', methods=['GET'])
@login_required
def doctor_patients():
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('/'))

    # Fetch search and filter parameters
    search_query = request.args.get('search', '').strip()
    filter_by = request.args.get('filter_by', 'recent')  # Default filter: recent
    sort_order = request.args.get('sort_order', 'desc')  # Default order: descending
    age_range = request.args.get('age_range')  # Example: "0-20", "21-40", etc.
    gender_filter = request.args.get('gender')  # Example: "Male", "Female", "Other"


    # Fetch patients linked to the logged-in doctor
    doctor_id = current_user.id
    doctor_patients = DoctorPatient.query.filter_by(doctor_id=doctor_id).all()
    patients_query = db.session.query(Patient).filter(Patient.id.in_([relation.patient_id for relation in doctor_patients]))

    # Apply search filter
    if search_query:
        patients_query = patients_query.filter(
            (Patient.patient_id.like(f"%{search_query}%")) |
            (Patient.firstname.like(f"%{search_query}%")) |
            (Patient.lastname.like(f"%{search_query}%"))
        )

    # Apply age range filter
    if age_range:
        min_age, max_age = map(int, age_range.split('-'))
        patients_query = patients_query.filter(Patient.age.between(min_age, max_age))

    # Apply gender filter
    if gender_filter:
        patients_query = patients_query.filter(Patient.gender == gender_filter)

    # Apply sorting filters
    if filter_by == 'recent':
        patients_query = patients_query.order_by(Patient.created_at.desc() if sort_order == 'desc' else Patient.created_at.asc())
    elif filter_by == 'name':
        patients_query = patients_query.order_by(Patient.firstname.asc() if sort_order == 'asc' else Patient.firstname.desc())

    # Get the final list of patients
    patients = patients_query.all()
    patient_form = PatientForm()


    return render_template('doctor_patients.html', 
                           patients=patients, 
                           patient_form=patient_form,
                           show_return_button=True, 
                           return_url=request.referrer)




# Visit Route 

@bp.route('/doctor/patient/<string:patient_id>', methods=['GET', 'POST'])
@login_required
def view_patient(patient_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    patient = Patient.query.options(
        joinedload(Patient.visits),
        joinedload(Patient.appointments),
        joinedload(Patient.immunizations),
        joinedload(Patient.allergies),
        joinedload(Patient.medications),
        joinedload(Patient.observations),
        joinedload(Patient.vitals),
        joinedload(Patient.procedures),
        joinedload(Patient.medical_history)
    ).filter_by(id=patient_id).first_or_404()

    lab_scan_groups = patient.lab_scan_groups
    additional_documents = AdditionalDocument.query.filter_by(patient_id=patient_id).all()

    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    # Get the latest appointment
    latest_appointments = (
        sorted(patient.appointments, key=lambda x: x.start, reverse=True)[:3]
        if patient.appointments else  []
    )
    
    # Map reason codes to their descriptions
    #reason_code_map = {item["code"]: item["display"] for item in Visit.get_reason_codes()}
    
    # Sort visits in descending order by visit_date and add reason descriptions
    sorted_visits = sorted(patient.visits, key=lambda visit: visit.visit_date, reverse=True)

    """
    for visit in patient.visits:
        visit.reason_code_description = reason_code_map.get(visit.reason_code, "Unknown Reason")

    """

    immunizationform = ImmunizationForm()
    medicationform = MedicationStatementForm()
    allergyform = AllergyIntoleranceForm()
    appointmentform=AppointmentForm()
    medicalhistoryform = MedicalHistoryForm()
    editmedicalhistoryform=MedicalHistoryForm()
    uploadform=UploadDocumentForm()
    visit_form = AddVisitForm()

    return render_template(
        'view_patient.html', 
        patient=patient, 
        visit=patient.visits,
        latest_appointments=latest_appointments,
        sorted_visits=sorted_visits,
        immunizations=patient.immunizations,
        allergies=patient.allergies,
        medications=patient.medications,
        medicalhistory=patient.medical_history, 
        lab_scan_groups = lab_scan_groups,
        immunizationform=immunizationform,
        medicationform = medicationform,
        appointmentform = appointmentform,
        allergyform = allergyform,
        medicalhistoryform=medicalhistoryform,
        editmedicalhistoryform=editmedicalhistoryform,
        additional_documents = additional_documents,
        uploadform = uploadform,
        visit_form=visit_form,
        show_return_button=True, 
        return_url=request.referrer
    )

@bp.route('/visit/<int:visit_id>', methods=['GET'])
@login_required
def view_visit(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))

    visit = Visit.query.options(
        joinedload(Visit.observations),
        joinedload(Visit.procedures),
        joinedload(Visit.medications),
        joinedload(Visit.vitals),
        joinedload(Visit.immunizations),
        joinedload(Visit.allergies),
        joinedload(Visit.medical_histories)
    ).filter_by(id=visit_id).first_or_404()

    # Ensure the doctor has access to this patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this visit.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    """
    reason_code_map = {item["code"]: item["display"] for item in Visit.get_reason_codes()}

    # Add the description to the visit object dynamically
    visit.reason_code_description = reason_code_map.get(visit.reason_code, "Unknown Reason")

    """
    

    # Initialize the immunization form with dynamic choices
    immunizationform = ImmunizationForm()
    medicationform=MedicationStatementForm()
    observationform = ObservationForm()
    allergyform = AllergyIntoleranceForm()
    appointmentform = AppointmentForm()
    vitalsform = VitalsForm()

    return render_template('view_visit.html', 
                           visit=visit,
                           immunizationform=immunizationform,
                           medicationform=medicationform, 
                           observationform=observationform,
                           allergyform = allergyform,
                           appointmentform = appointmentform,
                           vitalsform = vitalsform,
                           show_return_button=True, 
                            return_url=request.referrer)

@bp.route('/view_appointments')
@login_required
def view_appointments():
    # Get the current datetime to filter future appointments
    now = datetime.now()

    patient = Patient.query.filter_by(id=current_user.id).all()
    # Query all appointments for the current doctor and use joinedload to load the patient data
    all_appointments = Appointment.query.filter_by(doctor_id=current_user.id).options(joinedload(Appointment.patient)).all()
    

    # Filter and sort appointments by start time
    # Only include appointments that are in the future
    upcoming_appointments = [appointment for appointment in all_appointments if appointment.start > now]
    sorted_appointments = sorted(upcoming_appointments, key=lambda x: x.start)

    # Return the rendered template with the list of appointments
    return render_template('view_appointments.html', appointments=sorted_appointments, patient=patient)



# Add Medical Records Route

@bp.route('/doctor/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if current_user.role != 'doctor':
        flash('Access denied.')
        return redirect(url_for('dashboard'))

    patient_form = PatientForm()

    if patient_form.validate_on_submit():
        # Create a new Patient
        new_patient = Patient(
            firstname=patient_form.firstname.data,
            lastname=patient_form.lastname.data,
            age=patient_form.age.data,
            birthdate=patient_form.birthdate.data,
            gender=patient_form.gender.data,
            ecd_name=patient_form.ecd_name.data,
            ecd_contact_number=patient_form.ecd_contact_number.data,
            contact_number=patient_form.contact_number.data,
            home_address=patient_form.home_address.data,
        )
        db.session.add(new_patient)
        db.session.commit()  # Commit to generate new_patient.id

        # Create association in DoctorPatient
        doctor_patient = DoctorPatient(
            doctor_id=current_user.id,
            patient_id=new_patient.id
        )
        db.session.add(doctor_patient)
        db.session.commit()

        flash('New patient added successfully!', 'success')
        return redirect(url_for('main.doctor_patients'))

    return render_template('add_patient.html', 
                           patient_form=patient_form,
                           show_return_button=True, 
                            return_url=request.referrer)

@bp.route('/add_visit/<string:patient_id>', methods=['GET', 'POST'])
@login_required
def add_visit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    visit_form = AddVisitForm()

    # Populate dynamic fields using model methods
    visit_form.reason_code.choices = [(item["code"], item["display"]) for item in Visit.get_reason_codes()]
    visit_form.status.choices = [(item["code"], item["display"]) for item in Visit.get_status_codes()]
    visit_form.class_code.choices = [(item["code"], item["display"]) for item in Visit.get_class_codes()]
    visit_form.priority.choices = [(item["code"], item["display"]) for item in Visit.get_priority_codes()]
    visit_form.location.choices = [(item["code"], item["display"]) for item in Visit.get_locations()]


    if visit_form.validate_on_submit():
        # Create and save a new visit
        new_visit = Visit(
            patient_id=patient.id,
            doctor_id=current_user.id,  # Assuming logged-in user is the doctor
            visit_date=visit_form.visit_date.data,
            reason_code=visit_form.reason_code.data,
            diagnosis_code=visit_form.diagnosis_code.data,
            status=visit_form.status.data,
            class_code=visit_form.class_code.data,
            priority=visit_form.priority.data,
            location=visit_form.location.data,
            notes=visit_form.notes.data
        )
        db.session.add(new_visit)
        db.session.commit()
    
        flash('Encounter added successfully!', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    return render_template('add_visit.html', 
                           visit_form=visit_form, 
                           patient=patient,
                           show_return_button=True, 
                            return_url=request.referrer)

@bp.route('/patient/<int:visit_id>/add_immunization', methods=['POST', 'GET'])
@login_required
def add_immunization(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    # Load the visit object
    visit = Visit.query.get_or_404(visit_id)

    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add immunizations for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        vaccine_code = request.form.get('vaccine_code')
        status = request.form.get('status')
        date = request.form.get('date')
        lot_number = request.form.get('lot_number')
        site = request.form.get('site')
        route = request.form.get('route')
        dose_quantity = request.form.get('dose_quantity')
        manufacturer = request.form.get('manufacturer')
        notes = request.form.get('notes')
        
        # Create a new immunization instance
        immunization = Immunization(
            patient_id=visit.patient.id,
            visit_id=visit.id,
            vaccine_code=vaccine_code,
            status=status,
            date=date,
            lot_number=lot_number,
            site=site,
            route=route,
            dose_quantity=dose_quantity,
            manufacturer=manufacturer,
            notes=notes,
        )

        # Save to database
        db.session.add(immunization)
        db.session.commit()

        flash('Immunization added successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=visit.patient_id))

    # Pass the patient and form to the template
    return render_template(
        'add_immunization.html',
        patient=visit_id,
    )

@bp.route('/patient/<int:visit_id>/add_medication', methods=['POST', 'GET'])
@login_required
def add_medication(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))
    
    # Load the visit object
    visit = Visit.query.get_or_404(visit_id)
    
    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add immunizations for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        medication_code = request.form.get('medication_code')  # Medication code (e.g., RxNorm)
        medication_name = request.form.get('medication_name')  # Name or description of the medication
        status = request.form.get('status')  # e.g., "active", "completed"
        effectivePeriod_start = request.form.get('effectivePeriod_start')  # Start date of medication usage
        effectivePeriod_end = request.form.get('effectivePeriod_end')  # End date of medication usage
        date_asserted = request.form.get('date_asserted')  # Date when the statement was recorded
        information_source = request.form.get('information_source')  # Who reported the medication usage
        adherence = request.form.get('adherence')  # e.g., "compliant", "non-compliant"
        reason_code = request.form.get('reason_code')  # Reason for medication (e.g., "Hypertension")
        reason_reference = request.form.get('reason_reference')  # Reference to related condition or observation
        status_reason = request.form.get('status_reason')  # Reason for status change (e.g., "adverse reaction")
        dosage_instruction = request.form.get('dosage_instruction')  # Dosage instructions (e.g., "Take twice daily")
        notes = request.form.get('notes')  # Additional notes
        category = request.form.get('category', "outpatient")  # Default to "outpatient" if not provided
        route_of_administration = request.form.get('route_of_administration')  # Route (e.g., "oral", "IV")
        timing = request.form.get('timing')  # Timing of dosage (e.g., "twice daily")

        # Create a new MedicationStatement instance
        medication = MedicationStatement(
            patient_id=visit.patient.id,
            visit_id=visit.id,
            medication_code=medication_code,
            medication_name=medication_name,
            status=status,
            effectivePeriod_start=effectivePeriod_start,
            effectivePeriod_end=effectivePeriod_end,
            date_asserted=date_asserted,
            information_source=information_source,
            adherence=adherence,
            reason_code=reason_code,
            reason_reference=reason_reference,
            status_reason=status_reason,
            dosage_instruction=dosage_instruction,
            notes=notes,
            category=category,
            route_of_administration=route_of_administration,
            timing=timing,
        )

        # Save to database
        db.session.add(medication)
        db.session.commit()


        flash('Immunization added successfully.', 'success')
        return redirect(url_for('main.view_visit', visit_id=visit.id))

    # Pass the patient and form to the template
    return render_template(
        'view_visit.html',
        visit_id=visit.id,
    )

@bp.route('/patient/<int:visit_id>/add_allergy', methods=['POST', 'GET'])
@login_required
def add_allergy(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    # Load the visit object
    visit = Visit.query.get_or_404(visit_id)

    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add allergies for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        substance = request.form.get('substance')
        clinical_status = request.form.get('clinical_status')
        verification_status = request.form.get('verification_status')
        severity = request.form.get('severity')
        category = request.form.get('category')
        reaction = request.form.get('reaction')
        onset = request.form.get('onset')

        # Create a new allergy instance
        allergy = AllergyIntolerance(
            patient_id=visit.patient.id,
            visit_id=visit.id,
            substance=substance,
            clinical_status=clinical_status,
            verification_status=verification_status,
            severity=severity,
            category=category,
            reaction=reaction,
            onset=onset,
        )

        # Save to the database
        db.session.add(allergy)
        db.session.commit()

        flash('Allergy added successfully.', 'success')
        return redirect(url_for('main.view_visit', patient_id=visit.id))

    # Pass the patient and form to the template
    return render_template(
        'add_allergy.html',
        patient=visit_id,
    )

@bp.route('/patient/<int:visit_id>/add_observation', methods=['POST', 'GET'])
@login_required
def add_observation(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))
    
    # Load the visit object
    visit = Visit.query.get_or_404(visit_id)
    
    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add observations for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        code = request.form.get('code')  # Observation code (e.g., LOINC, SNOMED)
        value = request.form.get('value')  # Value of the observation (e.g., "98.6", "Normal")
        status = request.form.get('status')  # Status of the observation (e.g., "final")
        category = request.form.get('category', "vital-signs")  # Default to "vital-signs"
        effectiveDateTime = request.form.get('effectiveDateTime')  # Date/Time the observation was recorded

        # Create a new Observation instance
        observation = Observation(
            patient_id=visit.patient.id,
            visit_id=visit.id,
            code=code,
            value=value,
            status=status,
            category=category,
            effectiveDateTime=effectiveDateTime,
        )

        # Save to database
        db.session.add(observation)
        db.session.commit()

        flash('Observation added successfully.', 'success')
        return redirect(url_for('main.view_visit', visit_id=visit.id))

    # Pass the visit object and the form to the template
    return render_template(
        'view_visit.html',
        visit_id=visit.id,
        patient_id=visit.patient.id
    )

@bp.route('/patient/<int:visit_id>/add_vitals', methods=['POST', 'GET'])
@login_required
def add_vitals(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))
    
    # Load the visit object
    visit = Visit.query.get_or_404(visit_id)
    
    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add observations for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        status = request.form.get('status')  
        category = request.form.get('category', "vital-signs")  
        code = request.form.get('code')  
        effective_date = request.form.get('effective_date')  # Date/Time the observation was recorded
        value = request.form.get('value')  
        unit = request.form.get('unit')  
        
        # Create a new Vitals instance
        vitals = Vitals(
            patient_id=visit.patient.id,
            visit_id=visit.id,
            code=code,
            value=value,
            status=status,
            category=category,
            effective_date=effective_date,
        )

        # Save to database
        db.session.add(vitals)
        db.session.commit()

        flash('Vitals added successfully.', 'success')
        return redirect(url_for('main.view_visit', visit_id=visit.id))

    # Pass the visit object and the form to the template
    return render_template(
        'view_visit.html',
        visit_id=visit.id,
        patient_id=visit.patient.id
    )

@bp.route('/patient/<string:patient_id>/add_appointment', methods=['POST', 'GET'])
@login_required
def add_appointment(patient_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    # Load the visit object
    patient  = Patient.query.get_or_404(patient_id)

    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add appointments for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        start = request.form.get('start')
        end = request.form.get('end')
        status = request.form.get('status')
        service_category = request.form.get('service_category')
        service_type = request.form.get('service_type')
        specialty = request.form.get('specialty')
        appointment_type = request.form.get('appointment_type')
        priority = request.form.get('priority')
        participant_actor = request.form.get('participant_actor')
        participant_status = request.form.get('participant_status')
        reason_code = request.form.get('reason_code')

        # Create a new appointment instance
        appointment = Appointment(
            patient_id=patient.id,  # Taken from visit.patient.id
            doctor_id=current_user.id,  # Taken from current_user.id
            start=start,
            end=end,
            status=status,
            service_category=service_category,
            service_type=service_type,
            specialty=specialty,
            appointment_type=appointment_type,
            priority=priority,
            participant_actor=participant_actor,
            participant_status=participant_status,
            reason_code=reason_code,
        )

        # Save to database
        db.session.add(appointment)
        db.session.commit()

        flash('Appointment added successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    # Pass the visit and form to the template
    return render_template(
        'add_appointment.html',
        patient=patient,
    )

@bp.route('/patient/<string:patient_id>/add_medical_history', methods=['POST', 'GET'])
@login_required
def add_medical_history(patient_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    # Load the patient object
    patient  = Patient.query.get_or_404(patient_id)

    # Ensure the doctor has access to this visit's patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add medical history for this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Collect data from the form
        clinical_status = request.form.get('clinical_status')
        verification_status = request.form.get('verification_status')
        category = request.form.get('category')
        code = request.form.get('code')
        onset_date = request.form.get('onset_date')
        abatement_date = request.form.get('abatement_date')
        notes = request.form.get('notes')

        # Create a new appointment instance
        medicalhistory = MedicalHistory(
            patient_id=patient.id,  # Taken from visit.patient.id
            doctor_id=current_user.id,  # Taken from current_user.id
            clinical_status=clinical_status,
            verification_status=verification_status,
            category=category,
            code=code,
            onset_date=onset_date,
            abatement_date=abatement_date,
            notes=notes
        )

        # Save to database
        db.session.add(medicalhistory)
        db.session.commit()

        flash('Medication History added successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    # Pass the visit and form to the template
    return render_template(
        'add_appointment.html',
        patient=patient,
    )




# Edit Medical Records Route

@bp.route('/patient/<string:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    patient = Patient.query.filter_by(id=patient_id).first_or_404()
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to edit this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        # Retrieve only the fields being updated
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        entered_contact_number = request.form.get('contact_number')
        entered_home_address = request.form.get('home_address')
        entered_ecd_name = request.form.get('ecd_name')
        entered_ecd_contact_number = request.form.get('ecd_contact_number')

        # Update only the specific fields
        patient.firstname = firstname
        patient.lastname = lastname
        patient.contact_number = entered_contact_number
        patient.home_address = entered_home_address
        patient.ecd_name = entered_ecd_name
        patient.ecd_contact_number = entered_ecd_contact_number

        # Commit changes to the database
        db.session.commit()
        flash('Patient information updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    return render_template(
        'edit_patient.html',
        patient=patient,
        show_return_button=True,
        return_url=url_for('main.doctor_dashboard'),
    )

@bp.route('/visit/<int:visit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_visit(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    visit = Visit.query.filter_by(id=visit_id).first_or_404()
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to edit this visit.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    form = AddVisitForm(obj=visit)
    form.reason_code.choices = [(item["code"], item["display"]) for item in Visit.get_reason_codes()]
    form.status.choices = [(item["code"], item["display"]) for item in Visit.get_status_codes()]

    
    if form.validate_on_submit():
        visit.visit_date = form.visit_date.data
        visit.reason_code = form.reason_code.data
        visit.diagnosis_code = form.diagnosis_code.data
        visit.status = form.status.data
        visit.location = form.location.data
        visit.notes = form.notes.data

        db.session.commit()
        flash('Visit information updated successfully.', 'success')
        return redirect(url_for('main.view_visit', visit_id=visit.id))
    return render_template('edit_visits.html', 
                           form=form, 
                           visit=visit,
                           show_return_button=True, 
                            return_url=request.referrer)

@bp.route('/visit/<int:visit_id>/edit_vitals/<int:vitals_id>', methods=['GET', 'POST'])
@login_required
def edit_vitals(visit_id, vitals_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    vitals = Vitals.query.get_or_404(vitals_id)
    
    patient_id = vitals.patient_id
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=vitals.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Initialize the ObservationForm with the existing observation data
    vitals_form = VitalsForm(obj=vitals)
    
    if request.method == 'POST':
        # Collect data from the form
        status = request.form.get('status')  
        category = request.form.get('category', "vital-signs")  
        code = request.form.get('code')  
        effective_date = request.form.get('effective_date')  # Date/Time the observation was recorded
        value = request.form.get('value')  
        unit = request.form.get('unit')  

        # Update the observation with new data
        vitals.code = code
        vitals.value = value
        vitals.status = status
        vitals.category = category
        vitals.effective_date = effective_date
        vitals.unit = unit
        
        # Commit the changes to the database
        db.session.commit()

        flash('Vitals updated successfully.', 'success')
        return redirect(url_for('main.view_visit', visit_id=visit_id))
    
    # Render the form with existing observation data
    return redirect(url_for('main.view_visit', visit_id=visit_id))

@bp.route('/doctor/patient/<string:patient_id>/edit_observation/<int:observation_id>', methods=['GET', 'POST'])
@login_required
def edit_observation(patient_id, observation_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    patient = Patient.query.get_or_404(patient_id)
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    # Get the observation to be edited
    observation = Observation.query.get_or_404(observation_id)

    # Initialize the ObservationForm with the existing observation data
    observation_form = ObservationForm(obj=observation)
    
    if request.method == 'POST':
        # Collect data from the form
        code = request.form.get('code')
        value = request.form.get('value')
        status = request.form.get('status')
        category = request.form.get('category', "vital-signs")  # Default to "vital-signs"
        effectiveDateTime = request.form.get('effectiveDateTime')

        # Update the observation with new data
        observation.code = code
        observation.value = value
        observation.status = status
        observation.category = category
        observation.effectiveDateTime = effectiveDateTime
        
        # Commit the changes to the database
        db.session.commit()

        flash('Observation updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))
    
    # Render the form with existing observation data
    return render_template('edit_observation.html', observation_form=observation_form, patient=patient, observation=observation)


@bp.route('/doctor/patient/<string:patient_id>/edit_medication/<int:medication_id>', methods=['GET', 'POST'])
@login_required
def edit_medication(patient_id, medication_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    patient = Patient.query.get_or_404(patient_id)
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    medication = MedicationStatement.query.get_or_404(medication_id)
    
    form = MedicationStatementForm(obj=medication)  # Pre-populate form with existing medication data
    
    if request.method == 'POST':
        medication_code = request.form.get('medication_code')
        medication_name = request.form.get('medication_name')
        status = request.form.get('status')
        effectivePeriod_start = request.form.get('effectivePeriod_start')
        effectivePeriod_end = request.form.get('effectivePeriod_end')
        date_asserted = request.form.get('date_asserted')
        Adherence = request.form.get('Adherence')
        reason_code = request.form.get('reason_code')
        reason_reference = request.form.get('reason_reference')
        status_reason = request.form.get('status_reason')
        information_source = request.form.get('information_source')
        notes = request.form.get('notes')
        route_of_administration = request.form.get('route_of_administration')
        timing = request.form.get('timing')

        medication.medication_code = medication_code
        medication.medication_name = medication_name
        medication.status = status
        medication.effectivePeriod_start = effectivePeriod_start
        medication.effectivePeriod_end = effectivePeriod_end
        medication.date_asserted = date_asserted
        medication.Adherence = Adherence
        medication.reason_code = reason_code
        medication.reason_reference = reason_reference
        medication.status_reason = status_reason
        medication.information_source = information_source
        medication.notes = notes
        medication.route_of_administration = route_of_administration
        medication.timing = timing    
        
        
        db.session.commit()
        flash('Medication updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))
    
    return render_template('edit_medication.html', form=form, patient=patient, medication=medication)

@bp.route('/doctor/patient/<string:patient_id>/edit_immuinization/<int:immunization_id>', methods=['GET', 'POST'])
@login_required
def edit_immunization(patient_id, immunization_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    patient = Patient.query.get_or_404(patient_id)
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    immunization = Immunization.query.get_or_404(immunization_id)

    
    immunizationform = MedicationStatementForm(obj=immunization)  # Pre-populate form with existing medication data
    
    if request.method == 'POST':
        # Collect data from the form
        vaccine_code = request.form.get('vaccine_code')
        status = request.form.get('status')
        date = request.form.get('date')
        lot_number = request.form.get('lot_number')
        site = request.form.get('site')
        route = request.form.get('route')
        dose_quantity = request.form.get('dose_quantity')
        manufacturer = request.form.get('manufacturer')
        notes = request.form.get('notes')
        
        
        immunization.vaccine_code=vaccine_code
        immunization.status=status
        immunization.date=date
        immunization.lot_number=lot_number
        immunization.site=site
        immunization.route=route
        immunization.dose_quantity=dose_quantity
        immunization.manufacturer=manufacturer
        immunization.notes=notes
        
        db.session.commit()
        flash('Immunization updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))
    
    return render_template('edit_immunization.html', immunizationformform=immunizationform, patient=patient, immunization=immunization)

@bp.route('/doctor/patient/<string:patient_id>/edit_allergy/<int:allergy_id>', methods=['GET', 'POST'])
@login_required
def edit_allergy(patient_id, allergy_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    patient = Patient.query.get_or_404(patient_id)
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    allergy = AllergyIntolerance.query.get_or_404(allergy_id)

    allergyform = AllergyIntoleranceForm(obj=allergy)  # Pre-populate form with existing allergy data
    
    if request.method == 'POST':
        # Collect data from the form
        substance = request.form.get('substance')
        clinical_status = request.form.get('clinical_status')
        verification_status = request.form.get('verification_status')
        severity = request.form.get('severity')
        category = request.form.get('category')
        reaction = request.form.get('reaction')
        onset = request.form.get('onset')

        # Update allergy instance
        allergy.substance = substance
        allergy.clinical_status = clinical_status
        allergy.verification_status = verification_status
        allergy.severity = severity
        allergy.category = category
        allergy.reaction = reaction
        allergy.onset = onset

        # Commit changes to the database
        db.session.commit()
        flash('Allergy updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    return render_template('edit_allergy.html', allergyform=allergyform, patient=patient, allergy=allergy)

@bp.route('/doctor/patient/<string:patient_id>/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(patient_id, appointment_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))

    # Check if the patient is associated with the doctor
    patient = Patient.query.get_or_404(patient_id)
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Fetch the appointment object
    appointment = Appointment.query.get_or_404(appointment_id)

    # Pre-populate the form with existing appointment data
    appointmentform = AppointmentForm(obj=appointment)

    if request.method == 'POST':
        # Update data from the form
        appointment.start = request.form.get('start')
        appointment.end = request.form.get('end')
        appointment.status = request.form.get('status')
        appointment.service_category = request.form.get('service_category')
        appointment.service_type = request.form.get('service_type')
        appointment.specialty = request.form.get('specialty')
        appointment.appointment_type = request.form.get('appointment_type')
        appointment.priority = request.form.get('priority')
        appointment.reason_code = request.form.get('reason_code')

        # Commit changes to the database
        db.session.commit()
        flash('Appointment updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=appointment.patient_id))

    return render_template(
        'edit_appointment.html',
        appointmentform=appointmentform,
        patient=patient,
        appointment=appointment,
    )

@bp.route('/doctor/patient/<string:patient_id>/edit_medical_history/<int:medicalhistory_id>', methods=['GET', 'POST'])
@login_required
def edit_medical_history(patient_id, medicalhistory_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))

    # Check if the patient is associated with the doctor
    patient = Patient.query.get_or_404(patient_id)
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Fetch the appointment object
    medical_history = MedicalHistory.query.get_or_404(medicalhistory_id)

    # Pre-populate the form with existing appointment data
    editmedicalhistoryform = AppointmentForm(obj=medical_history)

    if request.method == 'POST':
        # Update data from the form
        medical_history.clinical_status = request.form.get('clinical_status')
        medical_history.verification_status = request.form.get('verification_status')
        medical_history.category = request.form.get('category')
        medical_history.code = request.form.get('code')
        medical_history.onset_date = request.form.get('onset_date')
        medical_history.abatement_date = request.form.get('abatement_date')
        medical_history.notes = request.form.get('notes')


        # Commit changes to the database
        db.session.commit()
        flash('Medical History updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    return render_template(
        'edit_appointment.html',
        editmedicalhistoryform=editmedicalhistoryform,
        patient=patient,
        medical_history=medical_history,
    )


# Delete Medical Records Route

@bp.route('/visit/<int:visit_id>/delete', methods=['POST'])
@login_required
def delete_visit(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))

    visit = Visit.query.get_or_404(visit_id)

    # Check if the doctor is associated with the patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to delete this visit.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    # Fetch patient associated with the visit
    patient = Patient.query.get_or_404(visit.patient_id)

    # Verify the name input
    entered_name = request.form.get('patient_name', '').strip()
    expected_name = f"{patient.firstname} {patient.lastname}"

    # Case-insensitive comparison to ensure exact match
    if entered_name.lower() != expected_name.lower():
        flash('Patient name does not match. Deletion aborted.', 'danger')
        return redirect(url_for('main.view_patient'))

    # Delete the visit
    db.session.delete(visit)
    db.session.commit()
    flash('Visit deleted successfully.', 'success')
    return redirect(url_for('main.view_patient', patient_id=visit.patient_id))

@bp.route('/patient/<string:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))

    patient = Patient.query.get_or_404(patient_id)

    # Check if the doctor is associated with the patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient.id).first()
    if not doctor_patient:
        flash('You do not have permission to delete this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    # Verify the name input
    entered_name = request.form.get('patient_name', '').strip()
    expected_name = f"{patient.firstname} {patient.lastname}"

    # Case insensitive comparison to ensure exact match
    if entered_name.lower() != expected_name.lower():
        flash('Patient name does not match. Deletion aborted.', 'danger')
        return redirect(url_for('main.doctor_patients'))

    # Delete the patient
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully.', 'success')
    return redirect(url_for('main.doctor_dashboard'))

@bp.route('/immunization/<int:immunization_id>/delete', methods=['POST'])
@login_required
def delete_immunization(immunization_id):
    # Fetch the immunization record or return a 404 if not found
    immunization = Immunization.query.get_or_404(immunization_id)
    visit = immunization.visit  # Assuming the `visit` relationship is set up correctly

    # Ensure the user has the appropriate permissions
    if not current_user.role == 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Delete the immunization record
    db.session.delete(immunization)
    db.session.commit()

    # Check if the associated visit contains any other medical records
    if (
        not visit.immunizations  # No immunizations left
        and not visit.vitals  # No vitals left
        and not visit.observations  # No observations left
        and not visit.procedures  # No procedures left
        and not visit.medications  # No medications left
        and not visit.allergies  # No allergies left
        and not visit.medical_histories  # No medical histories left
        and not visit.appointments  # No appointments left
    ):
        # If no related records are left, delete the visit
        db.session.delete(visit)
        db.session.commit()

        flash('Immunization and associated visit deleted successfully.', 'success')
    else:
        flash('Immunization deleted successfully.', 'success')

    # Redirect back to the patient's details page
    return redirect(url_for('main.view_patient', patient_id=immunization.patient_id))

@bp.route('/medication/<int:medication_id>/delete', methods=['POST'])
@login_required
def delete_medication(medication_id):
    # Fetch the immunization record or return a 404 if not found
    medication = MedicationStatement.query.get_or_404(medication_id)

    visit = medication.visit  # Assuming the `visit` relationship is set up correctly

    # Ensure the user has the appropriate permissions
    if not current_user.role == 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Delete the immunization record
    db.session.delete(medication)
    db.session.commit()

    # Check if the associated visit contains any other medical records
    if (
        not visit.immunizations  # No immunizations left
        and not visit.vitals  # No vitals left
        and not visit.observations  # No observations left
        and not visit.procedures  # No procedures left
        and not visit.immunizations  # No medications left
        and not visit.allergies  # No allergies left
        and not visit.medical_histories  # No medical histories left
        and not visit.appointments  # No appointments left
    ):
        # If no related records are left, delete the visit
        db.session.delete(visit)
        db.session.commit()

        flash('Immunization and associated visit deleted successfully.', 'success')
    else:
        flash('Immunization deleted successfully.', 'success')

    # Redirect back to the patient's details page
    return redirect(url_for('main.view_patient', patient_id=medication.patient_id))

@bp.route('/observation/<int:observation_id>/delete', methods=['POST'])
@login_required
def delete_observation(observation_id):
    # Fetch the immunization record or return a 404 if not found
    observation = Observation.query.get_or_404(observation_id)

    visit = observation.visit  # Assuming the `visit` relationship is set up correctly

    # Ensure the user has the appropriate permissions
    if not current_user.role == 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Delete the immunization record
    db.session.delete(observation)
    db.session.commit()

    # Check if the associated visit contains any other medical records
    if (
        not visit.immunizations  # No immunizations left
        and not visit.vitals  # No vitals left
        and not visit.medications  # No observations left
        and not visit.procedures  # No procedures left
        and not visit.immunizations  # No medications left
        and not visit.allergies  # No allergies left
        and not visit.medical_histories  # No medical histories left
        and not visit.appointments  # No appointments left
    ):
        # If no related records are left, delete the visit
        db.session.delete(visit)
        db.session.commit()

        flash('Immunization and associated visit deleted successfully.', 'success')
    else:
        flash('Immunization deleted successfully.', 'success')

    # Redirect back to the patient's details page
    return redirect(url_for('main.view_patient', patient_id=observation.patient_id))

@bp.route('/allergy/<int:allergy_id>/delete', methods=['POST'])
@login_required
def delete_allergy(allergy_id):
    # Fetch the allergy record or return a 404 if not found
    allergy = AllergyIntolerance.query.get_or_404(allergy_id)
    visit = allergy.visit  # Assuming the `visit` relationship is set up correctly

    # Ensure the user has the appropriate permissions
    if not current_user.role == 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Delete the allergy record
    db.session.delete(allergy)
    db.session.commit()

    # Check if the associated visit contains any other medical records
    if (
        not visit.immunizations  # No immunizations left
        and not visit.vitals  # No vitals left
        and not visit.observations  # No observations left
        and not visit.procedures  # No procedures left
        and not visit.medications  # No medications left
        and not visit.immunizations  # No allergies left
        and not visit.medical_histories  # No medical histories left
        and not visit.appointments  # No appointments left
    ):
        # If no related records are left, delete the visit
        db.session.delete(visit)
        db.session.commit()

        flash('Allergy and associated visit deleted successfully.', 'success')
    else:
        flash('Allergy deleted successfully.', 'success')

    # Redirect back to the patient's details page
    return redirect(url_for('main.view_patient', patient_id=allergy.patient_id))

@bp.route('/visit/<int:visit_id>/delete/<int:vitals_id>', methods=['POST'])
@login_required
def delete_vitals(vitals_id):
    # Fetch the allergy record or return a 404 if not found
    vitals = Vitals.query.get_or_404(vitals_id)
    visit = vitals.visit  # Assuming the `visit` relationship is set up correctly

    # Ensure the user has the appropriate permissions
    if not current_user.role == 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Delete the allergy record
    db.session.delete(vitals)
    db.session.commit()

    # Check if the associated visit contains any other medical records
    if (
        not visit.immunizations  # No immunizations left
        and not visit.vitals  # No vitals left
        and not visit.observations  # No observations left
        and not visit.procedures  # No procedures left
        and not visit.medications  # No medications left
        and not visit.immunizations  # No allergies left
        and not visit.medical_histories  # No medical histories left
        and not visit.appointments  # No appointments left
    ):
        # If no related records are left, delete the visit
        db.session.delete(visit)
        db.session.commit()

        flash('Allergy and associated visit deleted successfully.', 'success')
    else:
        flash('Allergy deleted successfully.', 'success')

    # Redirect back to the patient's details page
    return redirect(url_for('main.view_patient', patient_id=vitals.patient_id))

@bp.route('/appointment/<int:appointment_id>/delete', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    # Fetch the appointment record or return a 404 if not found
    appointment = Appointment.query.get_or_404(appointment_id)
    # Ensure the user has the appropriate permissions
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    # Delete the appointment record
    db.session.delete(appointment)
    db.session.commit()

    # Redirect back to the patient's details page
    return redirect(url_for('main.view_patient', patient_id=appointment.patient_id))


@bp.route('/patient/<string:patient_id>/delete_medical_history/<int:medicalhistory_id>', methods=['POST'])
@login_required
def delete_medical_history(patient_id, medicalhistory_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))

    patient = Patient.query.get_or_404(patient_id)
    medical_history = MedicalHistory.query.get_or_404(medicalhistory_id)

    # Check if the doctor is associated with the patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient.id).first()
    if not doctor_patient:
        flash('You do not have permission to delete this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    
    # Verify the name input
    entered_name = request.form.get('patient_name', '').strip()
    expected_name = f"{patient.firstname} {patient.lastname}"

    # Case insensitive comparison to ensure exact match
    if entered_name.lower() != expected_name.lower():
        flash('Patient name does not match. Deletion aborted.', 'danger')
        return redirect(url_for('main.doctor_patients'))

    # Delete the patient
    db.session.delete(medical_history)
    db.session.commit()
    flash('Patient deleted successfully.', 'success')
    return redirect(url_for('main.doctor_dashboard'))

def calculate_sus_score(responses):
    """
    Function to calculate the SUS score based on the responses.
    Args:
    - responses (list of int): The list of responses (1-5) to the survey questions.

    Returns:
    - float: The SUS score calculated using the provided responses.
    """
    # Calculate odd and even sums
    odd_sum = sum(responses[i - 1] - 1 for i in [1, 3, 5, 7, 9])  # Odd questions: subtract 1
    even_sum = sum(5 - responses[i - 1] for i in [2, 4, 6, 8, 10])  # Even questions: subtract from 5

    # SUS score formula
    sus_score = (odd_sum + even_sum) * 2.5
    return sus_score


@bp.route('/doctor/<string:doctor_id>/survey', methods=['GET', 'POST'])
@login_required
def survey(doctor_id):
    doctor = User.query.filter_by(id=doctor_id).first()
    if not doctor:
        flash("Doctor not found.", "error")
        return redirect(url_for('main.doctor_dashboard'))

    # Check if the survey has already been submitted by the user (allow overwriting)
    previous_response = SurveyResponse.query.filter_by(user_id=current_user.id).first()

    # Calculate the previous SUS score if a response already exists
    if previous_response:
        responses = [
            previous_response.q1, previous_response.q2, previous_response.q3,
            previous_response.q4, previous_response.q5, previous_response.q6,
            previous_response.q7, previous_response.q8, previous_response.q9,
            previous_response.q10
        ]
        sus_score = calculate_sus_score(responses)
    else:
        sus_score = None

    form = SurveyForm()

    if form.validate_on_submit():
        # Collect the responses
        responses = [
            int(form.q1.data), int(form.q2.data), int(form.q3.data), 
            int(form.q4.data), int(form.q5.data), int(form.q6.data), 
            int(form.q7.data), int(form.q8.data), int(form.q9.data), 
            int(form.q10.data)
        ]
        
        # Calculate SUS Score using the helper function
        sus_score = calculate_sus_score(responses)

        if previous_response:
            # Update the existing response if the survey has been submitted already
            previous_response.q1 = responses[0]
            previous_response.q2 = responses[1]
            previous_response.q3 = responses[2]
            previous_response.q4 = responses[3]
            previous_response.q5 = responses[4]
            previous_response.q6 = responses[5]
            previous_response.q7 = responses[6]
            previous_response.q8 = responses[7]
            previous_response.q9 = responses[8]
            previous_response.q10 = responses[9]
            previous_response.created_at = db.func.current_timestamp()  # Update timestamp to current time
        else:
            # Save a new survey response if it hasn't been submitted yet
            response = SurveyResponse(
                user_id=current_user.id,  # Only store the user_id (doctor will be identified as a user)
                q1=responses[0],
                q2=responses[1],
                q3=responses[2],
                q4=responses[3],
                q5=responses[4],
                q6=responses[5],
                q7=responses[6],
                q8=responses[7],
                q9=responses[8],
                q10=responses[9]
            )
            db.session.add(response)

        db.session.commit()  # Commit the changes to the database

        flash(f"Thank you for your feedback! Your SUS score is {sus_score:.2f}.", "success")
        return redirect(url_for('main.doctor_dashboard'))

    # If the form is not yet submitted, render the survey form
    return render_template('SUSForm.html', form=form, doctor=doctor, previous_response=previous_response, sus_score=sus_score)

@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if current_user.role != 'doctor':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)

    # Fetch user and education data
    user = User.query.get_or_404(current_user.id)
    education = UserEducation.query.filter_by(doctor_id=user.id).first()

    # Initialize the form
    form = UserUpdateProfile()

    # Ensure a default profile image is set
    if not user.profile_image:
        user.profile_image = 'image/default_profile.jpg'
        db.session.commit()

    # Handle form submission
    if form.validate_on_submit():

        # Update User fields
        new_username = form.username.data
        if new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username is already taken. Please choose a different one.', 'danger')
                return redirect(url_for('main.account'))
            user.username = new_username

        new_email = form.email.data
        if new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email is already in use. Please choose a different one.', 'danger')
                return redirect(url_for('main.account'))
            user.email = new_email

        user.contact_number = form.contact_number.data
        user.home_address = form.home_address.data
        user.ecd_name = form.ecd_name.data
        user.ecd_contact_number = form.ecd_contact_number.data
        user.country = form.country.data

        # Handle password changes
        if form.current_password.data or form.password.data or form.confirm_password.data:
            if not user.check_password(form.current_password.data):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('main.account'))
            if form.password.data != form.confirm_password.data:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('main.account'))
            if user.check_password(form.password.data):
                flash('New password must be different from the current password.', 'danger')
                return redirect(url_for('main.account'))
            user.set_password(form.password.data)

        # Update UserEducation fields
        if education:
            education.med_deg = form.med_deg.data
            education.med_deg_spec = form.med_deg_spec.data
            education.board_cert = form.board_cert.data
            education.license_number = form.license_number.data
            education.license_issuer = form.license_issuer.data
            education.license_expiration = form.license_expiration.data
            education.years_of_experience = form.years_of_experience.data
        else:
            # Create new education record if it doesn't exist
            education = UserEducation(
                doctor_id=user.id,
                med_deg=form.med_deg.data,
                med_deg_spec=form.med_deg_spec.data,
                board_cert=form.board_cert.data,
                license_number=form.license_number.data,
                license_issuer=form.license_issuer.data,
                license_expiration=form.license_expiration.data,
                years_of_experience=form.years_of_experience.data,
            )
            db.session.add(education)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.account'))

    # Populate form with data from User and UserEducation
    #if request.method == 'GET':
      #  form.username.data = user.username
       # form.email.data = user.email
        #form.contact_number.data = user.contact_number
    #    #form.home_address.data = user.home_address
#
 #       if education:
  #          form.med_deg.data = education.med_deg
   #         form.med_deg_spec.data = education.med_deg_spec
    #        form.board_cert.data = education.board_cert
     #       form.license_number.data = education.license_number
      #      form.license_issuer.data = education.license_issuer
       #     form.license_expiration.data = education.license_expiration
        #    form.years_of_experience.data = education.years_of_experience
    # Populate form with data from User and UserEducation
    if request.method == 'GET':
        for field_name, field in form._fields.items():
            if hasattr(user, field_name):
                field.data = getattr(user, field_name)
            elif education and hasattr(education, field_name):
                field.data = getattr(education, field_name)

    return render_template('doctor_account.html',
                            user=user, 
                            education=education,
                            form=form,
                            show_return_button=True, 
                            return_url=url_for('main.doctor_dashboard'))

@bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied: You do not have permission to view this page.')
        return redirect_dashboard(current_user.role)
    return render_template('admin_dashboard.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/upload_document/<string:patient_id>', methods=['GET', 'POST'])
def upload_document(patient_id):
    uploadform = UploadDocumentForm()
    if uploadform.validate_on_submit():
        document_name = uploadform.document_name.data
        document_file = uploadform.document_file.data
        
        # Save the file
        filename = secure_filename(document_file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        document_file.save(filepath)
        
        # Save to database
        new_document = AdditionalDocument(
            patient_id=patient_id,
            document_name=document_name,
            document_file=filename
        )
        db.session.add(new_document)
        db.session.commit()
        
        flash('Document uploaded successfully!', 'success')
        return redirect(url_for('main.patient_details', patient_id=patient_id))
    
    if uploadform.errors:
        flash('Error uploading document. Please check the form.', 'danger')

    return render_template('upload_document.html', uploadform=uploadform)

@bp.route('/upload_document_page/<string:patient_id>', methods=['GET', 'POST'])
def upload_document_page(patient_id):
    form = UploadDocumentForm()
    if form.validate_on_submit():
        document_name = form.document_name.data
        document_file = form.document_file.data
        
        # Save the file
        filename = secure_filename(document_file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        document_file.save(filepath)
        
        # Save to database
        new_document = AdditionalDocument(
            patient_id=patient_id,
            document_name=document_name,
            document_file=filename
        )
        db.session.add(new_document)
        db.session.commit()
        
        flash('Document uploaded successfully!', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient_id))
    
    return render_template('upload_document_page.html', form=form, patient_id=patient_id)


@bp.route('/download_document/<int:document_id>', methods=['GET'])
def download_document(document_id):
    document = AdditionalDocument.query.get(document_id)
    if not document:
        abort(404)

    # Assuming documents are stored in the configured UPLOAD_FOLDER
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, document.document_file)

    if not os.path.exists(filepath):
        abort(404)

    return send_from_directory(directory=upload_folder, path=document.document_file, as_attachment=True)


@bp.route('/create_lab_scan_group/<string:patient_id>', methods=['POST'])
def create_lab_scan_group(patient_id):
    group_name = request.form['group_name']
    if group_name:
        # Create the folder for lab scans
        new_group = LabScanGroup(group_name=group_name, patient_id=patient_id)
        db.session.add(new_group)
        db.session.commit()
        flash('Lab scan folder created successfully!', 'success')
    else:
        flash('Folder name cannot be empty.', 'danger')

    # Redirect back to patient details page
    return redirect(url_for('main.view_patient', patient_id=patient_id))


@bp.route('/view_lab_scans/<string:patient_id>/<int:group_id>',  methods=['GET', 'POST'])
def view_lab_scans(patient_id, group_id):
    patient = Patient.query.get(patient_id)
    group = LabScanGroup.query.get_or_404(group_id)  # Fetch the group by ID
    scans = group.scans  # Fetch all scans related to this group
    return render_template('view_lab_scans.html', group=group, scans=scans, patient=patient)

@bp.route('/upload_lab_scan/<string:patient_id>/<int:group_id>', methods=['POST'])
def upload_lab_scan(patient_id, group_id):
    # Ensure patient and group exist
    patient = Patient.query.get(patient_id)
    group = LabScanGroup.query.get(group_id)
    if not patient or not group:
        flash('Invalid patient or group ID', 'danger')
        return redirect(url_for('main.view_lab_scans', patient_id=patient_id, group_id=group_id))

    # Check if the form has a file
    if 'scan_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.view_lab_scans', patient_id=patient_id, group_id=group_id))

    scan_file = request.files['scan_file']

    # If no file is selected
    if scan_file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('main.view_lab_scans', patient_id=patient_id, group_id=group_id))

    # Ensure the file is allowed
    if scan_file and allowed_file(scan_file.filename):
        filename = secure_filename(scan_file.filename)
        file_path = os.path.join('lab_scans', filename)
        scan_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file_path))

        # Save the lab scan record to the database
        new_scan = LabScan(
            filename=filename,
            file_path=os.path.join('lab_scans', filename),  # Corrected file path here
            group_id=group.id
        )
        db.session.add(new_scan)
        db.session.commit()

        flash('Lab scan uploaded successfully!', 'success')
        return redirect(url_for('main.view_lab_scans', patient_id=patient.id, group_id=group.id))
    else:
        flash('Invalid file type. Only image files are allowed.', 'danger')
        return redirect(url_for('main.view_lab_scans', patient_id=patient.id, group_id=group.id))


@bp.route('/lab_scan_groups/<string:patient_id>', methods=['GET'])
def lab_scan_groups(patient_id):
    patient = Patient.query.get_or_404(patient_id)  # Fetch the patient
    lab_scan_groups = LabScanGroup.query.filter_by(patient_id=patient.id).all()  # Fetch all the lab scan groups for the patient
    return render_template('view_patient.html', patient=patient, lab_scan_groups=lab_scan_groups)

@bp.route('/download_lab_scan/<int:scan_id>', methods=['GET'])
def view_scan(scan_id):
    # Fetch the lab scan by its ID
    scan = LabScan.query.get(scan_id)
    if not scan:
        print(f"Scan with ID {scan_id} not found.")
        abort(404)
    
    # Construct the file path
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, scan.file_path)  # Corrected path

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        abort(404)
    
    # If everything is correct, send the file
    return send_from_directory(directory=upload_folder, path=scan.file_path, as_attachment=True)


@bp.route('/delete_lab_scan/<string:patient_id>/<int:scan_id>', methods=['POST'])
def delete_lab_scan(patient_id, scan_id):
    scan = LabScan.query.get_or_404(scan_id)  # Fetch the scan by ID
    group_id = scan.group_id  # Keep track of the group for redirection
    
    # Remove the scan from the database and the file system
    db.session.delete(scan)
    db.session.commit()
    
    # Optionally, delete the file from the file system
    try:
        os.remove(scan.file_path)  # Delete the file
    except FileNotFoundError:
        pass
    
    flash('Lab scan deleted successfully.', 'success')
    return redirect(url_for('main.view_lab_scans', patient_id = patient_id, group_id=group_id))


@bp.route('/delete_document/<string:patient_id>/<int:document_id>', methods=['POST'])
def delete_document(patient_id, document_id):
    # Fetch the document by its ID
    document = AdditionalDocument.query.get(document_id)
    if not document:
        flash('Document not found', 'danger')
        return redirect(url_for('main.view_patient', patient_id=patient_id))

    # Delete the document record from the database
    db.session.delete(document)
    db.session.commit()

    # Optionally, delete the file from the file system if it's stored
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, document.document_file)
    if os.path.exists(filepath):
        os.remove(filepath)

    flash('Document deleted successfully!', 'success')
    return redirect(url_for('main.view_patient', patient_id=patient_id))

@bp.route("/forgotpassword", methods=['GET', 'POST'])
def forgot_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)  # Send the reset email with token
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('main.forgot_password'))  # Redirect to the same page
        else:
            flash('No account found with that email. Please check your email or register.', 'danger')
            return redirect(url_for('main.forgot_password'))
    return render_template('forgot_password.html', form=form)

@bp.route("/verify_reset_token", methods=['POST'])
def verify_reset_token():
    token = request.form['token']
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired token. Please try again.', 'warning')
        return redirect(url_for('main.forgot_password'))

    # If valid, redirect to the reset password form
    return redirect(url_for('main.reset_password', token=token))

@bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.verify_reset_token(token):
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('main.forgot_password'))  # Redirect to forgot password page

    if request.method == 'POST':
        new_password = request.form['password']
        user.set_password(new_password)
        user.clear_reset_token()  # Clear the token once it is used
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.login'))  # Redirect to login after password reset

    return render_template('reset_password.html', token=token)


