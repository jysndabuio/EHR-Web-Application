import uuid
from datetime import datetime
from . import db  # Import db after it's initialized in __init__.py
from flask_login import UserMixin


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
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    id_card_number = db.Column(db.String(15), nullable=False)
    license_number = db.Column(db.String(15), nullable=False)
    home_address = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        return self.id
    
