from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy(app)

# User - Represents all users, including Admin, Customers, and Service Professionals.
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    service_requests = db.relationship('ServiceRequest', back_populates='customer', lazy=True)  # Link to customer requests
    reviews = db.relationship('Review', back_populates='customer', lazy=True)  # Link to customer reviews


# Service - Represents the types of services available in the platform.
class Service(db.Model):
    __tablename__ = 'Services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, default=30, nullable=False)  # Default to 30 minutes
    description = db.Column(db.Text, nullable=False)

    # Relationships
    service_professionals = db.relationship('ServiceProfessional', back_populates='service', lazy=True)  # Link to professionals
    service_requests = db.relationship('ServiceRequest', back_populates='service', lazy=True)  # Link to requests


# ServiceProfessional - Represents service professionals with their profiles and expertise.
class ServiceProfessional(db.Model):
    __tablename__ = 'ServiceProfessional'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_type = db.Column(db.Integer, db.ForeignKey('Services.id'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)  # Years of experience
    rating = db.Column(db.Float, nullable=True)  # Average rating
    is_verified = db.Column(db.Boolean, nullable=False, default=False)  # Verified by admin
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # Active or not

    # Relationships
    user = db.relationship('User', backref='professional_profile', lazy=True)  # Link to user
    service = db.relationship('Service', back_populates='service_professionals')  # Link to service type
    service_requests = db.relationship('ServiceRequest', back_populates='professional', lazy=True)  # Link to assigned requests
    reviews = db.relationship('Review', back_populates='professional', lazy=True)  # Link to reviews


# ServiceRequest - Tracks service requests, statuses, and remarks.
class ServiceRequest(db.Model):
    __tablename__ = 'ServiceRequest'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('Services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('ServiceProfessional.id'), nullable=True)  # Nullable initially
    date_of_request = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), nullable=False, default='requested')  # e.g., requested/assigned/closed
    remarks = db.Column(db.Text, nullable=True)

    # Relationships
    service = db.relationship('Service', back_populates='service_requests')  # Link to service type
    customer = db.relationship('User', back_populates='service_requests')  # Link to customer
    professional = db.relationship('ServiceProfessional', back_populates='service_requests')  # Link to professional


# Review - Stores customer reviews of service professionals.
class Review(db.Model):
    __tablename__ = 'Review'
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('ServiceRequest.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('ServiceProfessional.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    # Relationships
    professional = db.relationship('ServiceProfessional', back_populates='reviews')  # Link to professional
    customer = db.relationship('User', back_populates='reviews')  # Link to customer

with app.app_context():
    db.create_all()


    
