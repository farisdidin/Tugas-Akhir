from flask import Flask

app = Flask(__name__)

helo = "Ini dari file init"

from app import routes