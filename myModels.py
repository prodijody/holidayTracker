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
  system_role = db.Column(db.Integer)
  holidays_requests = db.relationship('HolidayRequest', backref='requester')
  holidays_quota = db.Column(db.Integer)

  def is_admin(self):
    admin_role = SystemRole.query.filter_by(name='Admin').first().id
    return self.system_role == admin_role

  def get_system_role(self):
    return SystemRole.query.filter_by(id=self.system_role).first()

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



class SystemRole(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(20), nullable=False)


class HolidayRequest(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  date_from = db.Column(db.DateTime())
  date_to = db.Column(db.DateTime())
  approved = db.Column(db.Boolean(), default=False)




# # Example relationship
# class Person(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(20))
#   pets = db.relationship('Pet', backref='owner')

# class Pet(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(20))
#   owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))

