from flask import Flask

app = Flask(__name__, template_folder='view')

helo = "Ini dari file init"

from app import routes