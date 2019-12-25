from app import db

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    device_ip = db.Column(db.String(100))
    device_repo_path = db.Column(db.String(100))
    device_version = db.Column(db.String(100))