from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import var
from app import routes

app = Flask(__name__, template_folder='view')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://didin:Underground23@localhost/tugas_akhir'
app.config['SQLALCHEMY_DATABASE_URI']= var.DATABASE
db = SQLAlchemy(app)


helo = "Ini dari file init"
