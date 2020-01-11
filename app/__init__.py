from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

from app import var

app = Flask(__name__, template_folder='view')
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://didin:Underground23@localhost/tugas_akhir'
app.config['SQLALCHEMY_DATABASE_URI']= var.DATABASE
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app.Models import User

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

from app import routes