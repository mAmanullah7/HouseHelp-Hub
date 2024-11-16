from app import app
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy(app)

class User(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    passhash=db.Column(db.String(120), nullable=False)
    name=db.Column(db.String(120), nullable=False)
    is_admin=db.Column(db.Boolean, nullable=False, default=False)

    




