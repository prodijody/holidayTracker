from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
from config_file import app_settings
import jwt

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = app_settings['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = app_settings['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = app_settings['SECURITY_PASSWORD_SALT']

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  creation_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
  name = db.Column(db.String(30), nullable=False)
  surname = db.Column(db.String(30))
  email = db.Column(db.String(20), unique=True, nullable=False)
  password = db.Column(db.String(85))
  confirmed = db.Column(db.Boolean(), default=False, nullable=False)
  confirmed_on = db.Column(db.DateTime(), nullable=True)


  def get_recover_password_token(self, expires_in=600):
    return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


  @staticmethod
  def verify_reset_password_token(token):
    try:
        id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    except:
        return
    return User.query.get(id)
