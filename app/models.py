import uuid
from datetime import datetime, date
from . import db, bcrypt  # Import db after it's initialized in __init__.py
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    role = db.Column(db.Enum("admin",  "doctor"), nullable=False) # to update patient should be default
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

    # Establish a one-to-many relationship with UserEducation
    education_records = relationship('UserEducation', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        return self.id
    
    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password, password)

class UserEducation(UserMixin, db.Model):
    __tablename__ = 'user_education'

    # Define the primary key for the UserEducation model
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key that links to the 'User' table
    user_id = db.Column(db.String(36), ForeignKey('users.id'), nullable=False)

    med_deg = db.Column(db.String(50), nullable=True)
    med_deg_spec = db.Column(db.String(50), nullable=True)
    board_cert = db.Column(db.String(50), nullable=True)
    license_number = db.Column(db.String(50), nullable=False)
    license_issuer = db.Column(db.String(50), nullable=True)
    license_expiration = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<UserEducation {self.med_deg} for {self.user_id}>'
    

    