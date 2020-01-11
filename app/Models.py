from app import db
from flask_login import UserMixin

class Device(db.Model):
    __tablename__='Device'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    device_ip = db.Column(db.String(100))
    device_repo_path = db.Column(db.String(100), nullable=True)
    device_version = db.Column(db.String(100), nullable=True)

class User(UserMixin, db.Model):
    __tablename__='User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    
    