import requests
import json
import os
from flask import url_for, render_template, flash, redirect, request, escape
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import desc
from myModels import app
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from werkzeug.utils import secure_filename
from myEmail import sendEmail, generate_confirmation_token, confirm_token
from forms import LoginForm


Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

moment = Moment(app)
from myModels import db, User

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# Unauthorised handler
@login_manager.unauthorized_handler
def unauthorized():
  flash('Please login to access your account.', 'info')
  return redirect(url_for('index'))








# Main route
@app.route('/')
@app.route('/home')
@app.route('/index', methods=['GET', 'POST'])
def index():
  if current_user.is_authenticated:
    return redirect(url_for('menu'))
  else:
    loginForm = LoginForm()
    if request.method == 'POST' and loginForm.validate_on_submit():
      escaped_email = escape(loginForm.email.data)
      user = User.query.filter_by(email=escaped_email).first()
      if user:
        if check_password_hash(user.password, loginForm.password.data):
          login_user(user)
          return redirect(url_for('menu'))
        else:
          flash('Wrong password or email.', 'info')
      else:
        flash('That email is not registered.','info')
      return redirect(url_for('index'))
    else:
      return render_template('index.html', form=loginForm)




# Menu route
@app.route('/menu', methods=['GET','POST'])
@login_required
def menu():
  return render_template('protected/menu.html')


# 404 route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# Logout route
@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user();
  return redirect(url_for('index'))



#Start app
if __name__ == '__main__':
  app.run(debug=True)
