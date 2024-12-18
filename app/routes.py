from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime
from .models import User, UserEducation, DoctorPatient, Patient, Visit, Appointment, Vitals, AllergyIntolerance, Observation,Immunization, Procedure,MedicalHistory, MedicationStatement
from .forms import RegisterForm,MedicationStatementForm,AllergyIntoleranceForm, AddVisitForm, PatientForm, VisitForm, ObservationForm, PasswordResetForm, UserUpdateProfile, PatientUpdateForm, ImmunizationForm, ProcedureForm, VitalsForm, MedicalHistoryForm
from . import db, bcrypt, mail
from .utils import verify_password_reset_token, generate_password_reset_token, allowed_file
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

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    form.role.data = 'doctor'  # Pre-set the role as "patient"

    if form.validate_on_submit():
        # Create a new User object with role set to "patient"
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


    return render_template('doctor_patients.html', 
                           patients=patients, 
                           show_return_button=True, 
                           return_url=request.referrer)


@bp.route('/doctor/patient/<string:patient_id>', methods=['GET', 'POST'])
@login_required
def view_patient(patient_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('login'))
    
    # Check if the patient is associated with the doctor
    patient = Patient.query.options(joinedload(Patient.visits), joinedload(Patient.appointments)).filter_by(id=patient_id).first_or_404()
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))
    # Get the latest appointment 
    latest_appointment = sorted(patient.appointments, key=lambda x: x.start, reverse=True)[0] if patient.appointments else None
    reason_code_map = {item["code"]: item["display"] for item in Visit.get_reason_codes()}

    # Sort visits in descending order by visit_date
    sorted_visits = sorted(patient.visits, key=lambda visit: visit.visit_date, reverse=True)

   # Add the description to each visit
    for visit in patient.visits:
        visit.reason_code_description = reason_code_map.get(visit.reason_code, "Unknown Reason")


    return render_template('view_patient.html', 
                           patient=patient, 
                           latest_appointment=latest_appointment,
                           sorted_visits = sorted_visits,
                           show_return_button=True, 
                            return_url=request.referrer)

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

    reason_code_map = {item["code"]: item["display"] for item in Visit.get_reason_codes()}

    # Add the description to the visit object dynamically
    visit.reason_code_description = reason_code_map.get(visit.reason_code, "Unknown Reason")

    return render_template('view_visit.html', 
                           visit=visit,
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
    
        flash('Visit, observations, and medications added successfully!', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))

    return render_template('add_visit.html', 
                           visit_form=visit_form, 
                           patient=patient,
                           show_return_button=True, 
                            return_url=request.referrer)


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
    if entered_name.lower() != entered_name.lower():
        flash('Patient name does not match. Deletion aborted.', 'danger')
        return redirect(url_for('main.doctor_patients'))

    # Delete the patient
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully.', 'success')
    return redirect(url_for('main.doctor_dashboard'))

    

@bp.route('/visit/<int:visit_id>/add_observation', methods=['GET', 'POST'])
@login_required
def add_observation(visit_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    visit = Visit.query.get_or_404(visit_id)

    # Ensure the doctor is associated with the patient
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to add observations for this visit.', 'danger')
        return redirect(url_for('main.view_visit', visit_id=visit_id))

    # Initialize the form and prepopulate hidden fields
    observation_form = ObservationForm()
    observation_form.visit_id.data = visit.id  # Populate visit_id
    observation_form.patient_id.data = visit.patient_id  # Populate patient_id

    if observation_form.validate_on_submit():
        try:
            # Debugging - Print form data
            print(f"Form Data: {observation_form.data}")

            new_observation = Observation(
                patient_id=visit.patient_id,
                visit_id=visit.id,
                code=observation_form.code.data,
                value=observation_form.value.data,
                status=observation_form.status.data,
            )
            db.session.add(new_observation)
            db.session.commit()

            flash('Observation added successfully!', 'success')
            return redirect(url_for('main.view_visit', visit_id=visit_id))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

    # Debugging - Print validation errors
    if observation_form.errors:
        print(f"Form Errors: {observation_form.errors}")

    return render_template('add_observation.html', 
                           observation_form=observation_form, 
                           visit=visit,
                           return_url=request.referrer)



@bp.route('/observation/<int:observation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_observation(observation_id):
    if current_user.role != 'doctor':
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('main.login'))

    observation = Observation.query.filter_by(id=observation_id).first_or_404()
    visit = observation.visit
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=current_user.id, patient_id=visit.patient_id).first()
    if not doctor_patient:
        flash('You do not have permission to edit this observation.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    form = ObservationForm(obj=observation)
    if form.validate_on_submit():
        observation.code = form.code.data
        observation.value = form.value.data
        observation.status = form.status.data
        observation.effectiveDateTime = form.effectiveDateTime.data

        db.session.commit()
        flash('Observation updated successfully.', 'success')
        return redirect(url_for('main.view_visit', visit_id=visit.id))
    return render_template('edit_observation.html', 
                           form=form, 
                           observation=observation,
                           show_return_button=True, 
                            return_url=request.referrer)


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

    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        patient.firstname = form.firstname.data
        patient.lastname = form.lastname.data
        patient.age = form.age.data
        patient.birthdate = form.birthdate.data
        patient.gender = form.gender.data
        patient.contact_number = form.contact_number.data
        patient.home_address = form.home_address.data
        patient.ecd_name = form.ecd_name.data
        patient.ecd_contact_number = form.ecd_contact_number.data

        db.session.commit()
        flash('Patient information updated successfully.', 'success')
        return redirect(url_for('main.view_patient', patient_id=patient.id))
    return render_template('edit_patient.html', 
                           form=form, 
                           patient=patient,
                           show_return_button=True, 
                            return_url=url_for('main.doctor_dashboard'))

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
        # Handle image upload
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            file = request.files['profile_image']
            if file and Config.allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    user.profile_image = f'image/{filename}'
                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'danger')
                    return redirect(url_for('main.account'))
            else:
                flash('Invalid file type. Please upload a valid image (JPG, PNG, GIF).', 'danger')
                return redirect(url_for('main.account'))

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

@bp.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate token and send password reset email
            token = generate_password_reset_token(user)
            reset_url = url_for('main.password_reset', token=token, _external=True)
            send_reset_email(user.email, reset_url)
            flash('Password reset email sent. Please check your inbox.')
        else:
            flash('Email not found.')
    return render_template('password_reset_request.html', form=form)

def send_reset_email(email, reset_url):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f"To reset your password, click the following link: {reset_url}\nIf you didn't make this request, please ignore this email."
    mail.send(msg)


@bp.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # Verify the token
    user_id = verify_password_reset_token(token)
    if not user_id:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.login'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        # Update the user's password
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('password_reset.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/forgotpassword')
def forgotpassword():
    return "Test"#

