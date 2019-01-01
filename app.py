import requests
import json
import os
from flask import url_for, render_template, flash, redirect, request, escape
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import desc, asc
from myModels import app
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from werkzeug.utils import secure_filename
from myEmail import sendEmail, generate_confirmation_token, confirm_token
from forms import LoginForm, RecoverPasswordForm, ResetPasswordForm, AddUserForm, RequestHolidaysForm, UpdateHolidaysRequest, UpdateUserForm
from config_file import random_string

Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

moment = Moment(app)
from myModels import db, User, SystemRole, HolidayRequest

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
    resetPasswordForm = RecoverPasswordForm()
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

    elif request.method == 'POST' and resetPasswordForm.validate_on_submit():
      email = escape(resetPasswordForm.email.data)
      user = User.query.filter_by(email=email).first()
      if user:
        recover_token = user.get_recover_password_token()
        url = url_for('recover_password', recover_token=recover_token, _external=True)
        html = render_template('email_templates/reset_password.html', confirm_url=url)
        sendEmail(email_subject='Reset your password',
                  recipients=[email],
                  email_html=html)
        flash('An email has been sent with a reset link. Follow the link to reset your password within the next 10 minutes.','info')
      else:
        flash('That email is not registered.','info')
      return redirect(url_for('index'))
    else:
      return render_template('public/index.html', form=loginForm, form2=resetPasswordForm)


@app.route('/recover_password/<recover_token>', methods=['GET','POST'])
def recover_password(recover_token):
  if current_user.is_authenticated:
    return redirect(url_for('menu'))
  else:
    verify_token = User.verify_reset_password_token(recover_token)
    if not verify_token:
      flash('This reset link is invalid or has expired. Request a new one.', 'info')
      return redirect(url_for('index'))

    form = ResetPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():

      if form.password.data != form.password2.data:
        flash('Those passwords did not match. Try again!','danger')
        return redirect(url_for('recover_password', recover_token=recover_token))
      else:
        user = verify_token
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You may now login.', 'success')
        return redirect(url_for('index'))
    return render_template('public/reset_password.html', form=form, token=recover_token)


# Menu route
@app.route('/menu', methods=['GET','POST'])
@login_required
def menu():
  if current_user.is_admin():
    pending_requests = len(HolidayRequest.query.filter_by(status='Pending').all())

    if pending_requests > 0:
      flash('You have <strong>{}</strong> holiday request(s) waiting for un update. <a href="{}">Click here</a>.'.format(pending_requests, url_for('admin')),'info')

  return render_template('protected/menu.html')


# Calendar route
@app.route('/calendar', methods=['GET','POST'])
@login_required
def calendar():
  requests = HolidayRequest.query.filter_by(status='Approved').order_by(HolidayRequest.date_from.asc()).all()
  requests_for_calendar = [{'title' : i.get_user().name + ' ' + i.get_user().surname, 'start' : str(i.date_from), 'end' : str(i.date_to), 'url': url_for('open_request', request_id=i.id)} for i in requests]
  return render_template('protected/calendar.html', requests=requests, requests_for_calendar=requests_for_calendar)


@app.route('/request_holidays', methods=['GET','POST'])
@login_required
def request_holidays():
  requestHolidaysForm = RequestHolidaysForm()
  if request.method == 'POST' and requestHolidaysForm.validate_on_submit():
    # escape form input and convert string to date
    date_format = "%Y-%m-%d"

    date_from = datetime.strptime(escape(requestHolidaysForm.date_from.data), date_format)
    date_to = datetime.strptime(escape(requestHolidaysForm.date_to.data), date_format)
    comment = escape(requestHolidaysForm.comment.data)

    # do some checking before anything else

    # add request to DB
    new_request = HolidayRequest(
      user_id=current_user.id,
      date_from=date_from,
      date_to=date_to,
      comment=comment,
      status='Pending')
    db.session.add(new_request)
    db.session.commit()

    # email user
    html = render_template('email_templates/user_holiday_request.html', date_from=date_from, date_to=date_to, comment=comment)
    sendEmail(email_subject='Your holiday request', recipients=[current_user.email], email_html=html)

    # email manager
    user = current_user.name + ' ' + current_user.surname
    html2 = render_template('email_templates/admin_holiday_request.html', date_from=date_from, date_to=date_to, comment=comment, user=user)
    ADMIN_ROLE = SystemRole.query.filter_by(name='Admin').first().id
    THE_ADMIN = User.query.filter_by(system_role=ADMIN_ROLE).first().email
    sendEmail(email_subject='NEW holiday request', recipients=[THE_ADMIN], email_html=html2)

    flash('Your request has been submitted. An email has been sent to you and your manager.','success')
    return redirect(url_for('request_holidays'))

  return render_template('protected/request_holidays.html', form=requestHolidaysForm)


@app.route('/calendar/request/<request_id>', methods=['GET','POST'])
@login_required
def open_request(request_id):
  req = escape(request_id)
  request_exists = HolidayRequest.query.get(req)
  if request_exists:
    if request_exists.user_id == current_user.id or current_user.is_admin():
      form = RequestHolidaysForm(obj=request_exists)

      if request.method == 'POST' and form.validate_on_submit():
        request_exists.date_from = form.date_from.data
        request_exists.date_to = form.date_to.data
        request_exists.comment = form.comment.data
        db.session.commit()
        flash('Your request has been updated successfuly.','success')
        return redirect(url_for('open_request', request_id=request_id))

      return render_template('protected/open_request.html', request=request_exists, form=form)
    else:
      flash('Noting to see here, details of that holiday request are private.','info')
      return redirect(url_for('calendar'))
  else:
    flash('That request id {} is invalid.'.format(request_id),'danger')
    return redirect(url_for('calendar'))


#############
#'''Admin'''#
#############

# Admin route
@app.route('/staff', methods=['GET'])
@login_required
def admin():
  if not current_user.is_admin():
    flash('That area is restricted to admins.','info')
    return redirect(url_for('menu'))

  staff_members = User.query.all()
  return render_template('protected/admin/staff_list.html', staff_members=staff_members)

# Admin user route
@app.route('/admin/user/<user_id>', methods=['GET','POST'])
@login_required
def admin_user(user_id):
  if not current_user.is_admin():
    flash('That area is restricted to admins.','info')
    return redirect(url_for('menu'))

  user_id = escape(user_id)
  user = User.query.get(user_id)
  if user:
    form2 = UpdateUserForm(obj=user)
    form2.system_role.choices = [(i.id, str(i.id) + ') ' + i.name) for i in SystemRole.query.order_by(SystemRole.id.desc()).all()]

    form = UpdateHolidaysRequest()
    form.request.choices = [(0, 'Select one')] + [(i.id, i.id) for i in HolidayRequest.query.filter_by(user_id=user_id).all()]

    if request.method == 'POST' and form.validate_on_submit():
      request_id = escape(form.request.data)
      status = escape(form.status.data)
      comment = escape(form.manager_comment.data)

      find_request = HolidayRequest.query.get(request_id)
      if not find_request or status not in ['Approved', 'Cancelled', 'Pending','Declined']:
        flash('Please choose from the list a request ID and a status.','danger')
        return redirect(url_for('admin'))
      else:
        find_request.status = status
        find_request.manager_comment = comment
        db.session.commit()
        flash('Holiday request updated successfuly. An email has been sent to the staff member.','success')

        html = render_template('email_templates/request_updated.html', date_from=find_request.date_from, date_to=find_request.date_to, comment=find_request.comment, status=find_request.status, manager_comment=find_request.manager_comment)
        sendEmail(email_subject='Update to your holiday request', recipients=[user.email], email_html=html)

        return redirect(url_for('admin'))

    return render_template('protected/admin/admin_user.html', user=user, form=form, form2=form2)
  else:
    flash('User id {user_id} does not exist.'.format(user_id=user_id), 'danger')
    return redirect(url_for('admin'))

# Admin update user route
@app.route('/admin/user/update_user/<user_id>', methods=['GET','POST'])
@login_required
def update_user(user_id):
  if not current_user.is_admin():
    flash('That area is restricted to admins.','info')
    return redirect(url_for('menu'))

  user_id = escape(user_id)
  user = User.query.get(user_id)
  if user:
    form2 = UpdateUserForm()
    form2.system_role.choices = [(i.id, str(i.id) + ') ' + i.name) for i in SystemRole.query.order_by(SystemRole.id.desc()).all()]
    if request.method == 'POST' and form2.validate_on_submit():
      user.name = escape(form2.name.data)
      user.surname = escape(form2.surname.data)
      user.email = escape(form2.email.data)
      user.system_role = escape(form2.system_role.data)
      user.holidays_quota = escape(form2.holidays_quota.data)

      db.session.commit()
      flash('User updated successfuly.','success')
      return redirect(url_for('admin_user', user_id=user_id))

  flash('That user id is not valid.', 'danger')
  return redirect(url_for('admin_user', user_id=user_id))

# Add user route
@app.route('/add_user', methods=['GET','POST'])
@login_required
def add_user():
  if not current_user.is_admin():
    flash('That area is restricted to admins.','info')
    return redirect(url_for('menu'))

  existing_users = User.query.all()
  addUserForm = AddUserForm()
  addUserForm.system_role.choices = [(i.id, str(i.id) + ') ' + i.name) for i in SystemRole.query.order_by(SystemRole.id.desc()).all()]
  if request.method == 'POST' and addUserForm.validate_on_submit():
    # escape form input
    name = escape(addUserForm.name.data)
    surname = escape(addUserForm.surname.data)
    email = escape(addUserForm.email.data)
    system_role = escape(addUserForm.system_role.data)
    holidays_quota = escape(addUserForm.holidays_quota.data)

    # check email exists
    email_exists = User.query.filter_by(email=email).first()
    if email_exists:
      flash('That email is already registered.','danger')
      return redirect(url_for('add_user'))

    # add user to db
    new_user = User(
      name=name,
      surname=surname,
      email=email,
      password=generate_password_hash(random_string['_'], method='sha256'),
      system_role=system_role,
      holidays_quota=holidays_quota)
    db.session.add(new_user)
    db.session.commit()

    # prepare and send email to reset password
    recover_token = new_user.get_recover_password_token()
    url = url_for('recover_password', recover_token=recover_token, _external=True)
    html = render_template('email_templates/reset_password.html', confirm_url=url)
    sendEmail(email_subject='Confirm your account and reset your password.', recipients=[email], email_html=html)
    flash('User added successfuly! An email has been sent to {email} with instructions to reset the password.'.format(email=email),'success')
    return redirect(url_for('add_user'))

  return render_template('protected/admin/add_user.html', form=addUserForm, existing_users=existing_users)


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
