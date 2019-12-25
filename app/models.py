from app import db

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column()
    device_ip = db.Column()
    device_repo_path = db.Column()
    device_version = db.Column()