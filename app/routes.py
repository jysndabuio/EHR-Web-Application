from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime
from .models import User, UserEducation, DoctorPatient, Patient, Vitals, AllergyIntolerance, Observation,Immunization, Procedure,MedicalHistory, MedicationStatement
from .forms import RegisterForm, PasswordResetForm, UserUpdateProfile, PatientUpdateForm, ImmunizationForm, ProcedureForm, VitalsForm, MedicalHistoryForm
from . import db, bcrypt, mail
from .utils import verify_password_reset_token, generate_password_reset_token, allowed_file
from .config import Config
from werkzeug.utils import secure_filename
import os

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

@bp.route('/patients', methods=['GET', 'POST'])
@login_required
def doctor_patients():
    if current_user.role != 'doctor':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    # Fetch patients linked to the logged-in doctor
    doctor_id = current_user.id
    doctor_patients = DoctorPatient.query.filter_by(doctor_id=doctor_id).all()
    patients = [relation.patient for relation in doctor_patients]

    # Form for adding new patients
    patient_form = PatientUpdateForm()

    if patient_form.validate_on_submit():
        # Create a new patient and associate with the doctor
        new_patient = Patient(
            firstname=patient_form.firstname.data,
            lastname=patient_form.lastname.data,
            contact_number=patient_form.contact_number.data,
            home_address=patient_form.home_address.data,
            doctor_relationships=[DoctorPatient(doctor_id=doctor_id)],  # Many-to-many link
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('New patient added successfully!', 'success')
        return redirect(url_for('main.doctor_patients'))

    return render_template('doctor_patients.html', 
                           patients=patients, 
                           patient_form=patient_form,
                           show_return_button=True, 
                           return_url=url_for('main.doctor_dashboard'))

@bp.route('/doctor/patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def patient_details(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Fetch related data
    immunizations = patient.immunizations.all()
    procedures = patient.procedures.all()
    vitals = patient.vitals.all()
    medical_history = patient.medical_history.all()

    # Forms for CRUD operations
    patient_form = PatientUpdateForm(obj=patient)
    immunization_form = ImmunizationForm()
    procedure_form = ProcedureForm()
    vitals_form = VitalsForm()
    history_form = MedicalHistoryForm()

    # Handle Patient Update
    if patient_form.validate_on_submit():
        patient.firstname = patient_form.firstname.data
        patient.lastname = patient_form.lastname.data
        patient.contact_number = patient_form.contact_number.data
        patient.home_address = patient_form.home_address.data
        db.session.commit()
        flash('Patient details updated successfully!', 'success')
        return redirect(url_for('patient_details', patient_id=patient.id))

    # Handle Adding Immunization
    if immunization_form.validate_on_submit():
        new_immunization = Immunization(
            patient_id=patient.id,
            vaccine_code=immunization_form.vaccine_code.data,
            status=immunization_form.status.data,
            date=immunization_form.date.data,
        )
        db.session.add(new_immunization)
        db.session.commit()
        flash('New immunization added!', 'success')
        return redirect(url_for('patient_details', patient_id=patient.id))

    # Handle Adding Procedure
    if procedure_form.validate_on_submit():
        new_procedure = Procedure(
            patient_id=patient.id,
            code=procedure_form.code.data,
            status=procedure_form.status.data,
            performed_date=procedure_form.performed_date.data,
        )
        db.session.add(new_procedure)
        db.session.commit()
        flash('New procedure added!', 'success')
        return redirect(url_for('patient_details', patient_id=patient.id))

    # Handle Adding Vitals
    if vitals_form.validate_on_submit():
        new_vitals = Vitals(
            patient_id=patient.id,
            type=vitals_form.type.data,
            value=vitals_form.value.data,
            unit=vitals_form.unit.data,
            date_recorded=vitals_form.date_recorded.data,
        )
        db.session.add(new_vitals)
        db.session.commit()
        flash('New vitals recorded!', 'success')
        return redirect(url_for('patient_details', patient_id=patient.id))

    # Handle Adding Medical History
    if history_form.validate_on_submit():
        new_history = MedicalHistory(
            patient_id=patient.id,
            condition=history_form.condition.data,
            onset_date=history_form.onset_date.data,
            resolution_date=history_form.resolution_date.data,
            notes=history_form.notes.data,
        )
        db.session.add(new_history)
        db.session.commit()
        flash('New medical history added!', 'success')
        return redirect(url_for('patient_details', patient_id=patient.id))

    return render_template(
        'patient_details.html',
        patient=patient,
        immunizations=immunizations,
        procedures=procedures,
        vitals=vitals,
        medical_history=medical_history,
        patient_form=patient_form,
        immunization_form=immunization_form,
        procedure_form=procedure_form,
        vitals_form=vitals_form,
        history_form=history_form,
    )

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

