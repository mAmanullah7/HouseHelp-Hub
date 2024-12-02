from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db=SQLAlchemy(app)

# User - Represents all users, including Admin, Clients, and Service Providers
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  # User's unique username
    passhash = db.Column(db.String(120), nullable=False)  # Hashed password for authentication
    name = db.Column(db.String(120), nullable=False)  # User's full name
    address = db.Column(db.String(120), nullable=True)  # User's address
    service_type = db.Column(db.String(120), nullable=True)  # Type of service offered
    pincode = db.Column(db.Integer, nullable=True)  # Postal code
    avg_rating = db.Column(db.Float, default=0.0, nullable=False)  # Average rating for the user
    rating_count = db.Column(db.Integer, default=0, nullable=False)  # Number of ratings received
    experience = db.Column(db.String(120), nullable=True)  # Provider's experience
    documents = db.Column(db.String(120), nullable=True)  # Uploaded documents for verification
    is_admin = db.Column(db.Boolean, default=False)  # Indicates if the user is an admin
    is_client = db.Column(db.Boolean, default=False)  # Indicates if the user is a client
    is_provider = db.Column(db.Boolean, default=False)  # Indicates if the user is a provider
    is_verified = db.Column(db.Boolean, default=False)  # Indicates if the provider is verified
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)  # Foreign key to the services table
    is_blocked = db.Column(db.Boolean, default=False)
    # Relationships
    service = db.relationship('Service', back_populates="providers")
    client_requests = db.relationship('ServiceRequest', back_populates='client', foreign_keys="ServiceRequest.client_id")
    provider_requests = db.relationship('ServiceRequest', back_populates='provider', foreign_keys="ServiceRequest.provider_id")

    def update_rating(self, new_rating):
        total_rating = (self.avg_rating * self.rating_count) + new_rating
        self.rating_count += 1
        self.avg_rating = total_rating / self.rating_count
        
    def toggle_block(self):
        self.is_blocked = not self.is_blocked
        # db.session.commit()



class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), unique=True, nullable=False)  # Name of the service
    description = db.Column(db.String(120), nullable=True)  # Service description
    price = db.Column(db.Integer, nullable=True)  # Base price
    time_required = db.Column(db.String(120), nullable=True)  # Estimated time for the service
    requests = db.relationship('ServiceRequest', back_populates="service")
    providers = db.relationship('User', back_populates="service")


class ServiceRequest(db.Model):
    __tablename__ = "serviceRequest"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    req_type = db.Column(db.String(120), nullable=False)  # Request type (e.g., repair, installation)
    description = db.Column(db.Text, nullable=True)  # Detailed request description
    status = db.Column(db.String(120), nullable=True)  # Current request status
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Creation timestamp
    date_closed = db.Column(db.DateTime, nullable=True)  # Closing timestamp
    rating_by_client = db.Column(db.Float, default=0.0, nullable=False)  # Rating by the client
    review_by_client = db.Column(db.String(120), nullable=True)  # Review comments by the client

    # Relationships
    service = db.relationship('Service', back_populates="requests")
    client = db.relationship('User', back_populates="client_requests", foreign_keys=[client_id])
    provider = db.relationship('User', back_populates="provider_requests", foreign_keys=[provider_id])


class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    activity_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    request_id = db.Column(db.Integer, db.ForeignKey('serviceRequest.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    reported = db.Column(db.Boolean, default=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('serviceRequest.id'))
    reported_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    issue_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Open')

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        passhash = generate_password_hash('admin')
        admin=User(username ='admin', passhash=passhash,name='Admin',is_admin=True)
        db.session.add(admin)
        db.session.commit()



    
