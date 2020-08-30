import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS", "api.server.config.DevelopmentConfig")
print(app_settings)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

