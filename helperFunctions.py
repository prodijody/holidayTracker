from myModels import db, User, SystemRole, HolidayRequest
from app import generate_password_hash
from config_file import admin_user, random_string

def drop_then_create_all():
  db.drop_all()
  db.create_all()
  return

def create_system_roles():
  admin_role = SystemRole(name='Admin')
  user_role = SystemRole(name='User')
  db.session.add(admin_role)
  db.session.add(user_role)
  db.session.commit()
  return

def create_system_admin():
  admin_role = SystemRole.query.filter_by(name='Admin').first().id
  system_admin = User(
    name=admin_user['NAME'],
    surname=admin_user['SURNAME'],
    system_role=admin_role,
    email=admin_user['EMAIL'],
    password=generate_password_hash(admin_user['APP_PASSWORD'], method='sha256'),
    holidays_quota=admin_user['HOLIDAYS_QUOTA'])
  db.session.add(system_admin)
  db.session.commit()
  return

def restartDB():
  drop_then_create_all()
  create_system_roles()
  create_system_admin()
  return

if __name__ == "__main__":
  restartDB()