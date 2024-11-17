from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy(app)

# User - A user of the application Represents all users, including Admin, Customers, and Service Professionals.
class User(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    passhash=db.Column(db.String(120), nullable=False)
    name=db.Column(db.String(120), nullable=False)
    is_admin=db.Column(db.Boolean, nullable=False, default=False)


# Service Professional - A service professional in the application
# Represents the types of services available in the platform. Each service will be created by the Admin.
class Service(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(120), nullable =False, unique=True)
    price=db.Column(db.Float, nullable=False)
    time_required=db.Column(db.Integer,default=db.func.current_timestamp(), nullable =False)
    description=db.Column(db.Text, nullable=False)

# Service Professional - Represents service professionals with their profiles and expertise.

class ServiceProfessional(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    date_created=db.Column(db.DateTime, default= db.func.current_timestamp(), nullable=False)
    description=db.Column(db.Text, nullable=False)
    service_type=db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    exprerience=db.Column(db.Integer, nullable=False)    #yeas of experience
    description=db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=True)  #averaege rating 
    is_verified= db.Column(db.Boolean, nullable=False, default=False)  #verified by admin
    is_active= db.Column(db.Boolean, nullable=False, default=True)  #active or not



