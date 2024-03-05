from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    company_code = db.Column(db.String(3), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True)
    mobile = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(150))
    establishment_year = db.Column(db.String(4))
    employees = db.relationship('Employee', backref='user', lazy=True)
    roles= db.relationship('Role', backref='user', lazy=True)

class Employee(db.Model):
    employee_id = db.Column(db.String(15), primary_key=True)
    first_name = db.Column(db.String(150))
    middle_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    mobile = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
  
class Role(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    employees = db.relationship('Employee', backref='role', lazy=True)
    


'''

class Role(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  role = db.Column(db.String(50), unique=True)
  description = db.Column(db.String(255))


class Employee(db.Model):
  employee_id = db.Column(db.String(15), primary_key=True)
  first_name = db.Column(db.String(150))
  middle_name = db.Column(db.String(150))
  last_name = db.Column(db.String(150))
  email = db.Column(db.String(150), unique=True)
  mobile = db.Column(db.Integer)
  role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

  
class Company(db.Model, UserMixin):
  company_code = db.Column(db.String(3), primary_key=True, nullable=False)
  company_name = db.Column(db.String(150))
  establishment_year = db.Column(db.Integer)
  email = db.Column(db.String(150), unique=True)
  password = db.Column(db.String(150))
  mobile = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  
class Company(db.Model, UserMixin):
  company_id = db.Column(db.Integer, primary_key=True)
  role = db.Column(db.String(150), db.ForeignKey('role.role_type'))
  company_name = db.Column(db.String(150))
  establishment_date = db.Column(db.Date)
  email = db.Column(db.String(150), unique=True)
  password = db.Column(db.String(150))
  mobile = db.Column(db.Integer)
  superadmin_id = db.Column(db.Integer, db.ForeignKey('superadmin.id'))
  employee = db.relationship('Employee')
  role = db.relationship('Role')

  
class Superadmin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    company = db.relationship('Company')

class Company(db.Model, UserMixin):
    company_id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(150), db.ForeignKey('role.role_type'))
    company_name = db.Column(db.String(150))
    establishment_date = db.Column(db.Date)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    mobile = db.Column(db.Integer)
    superadmin_id = db.Column(db.Integer, db.ForeignKey('superadmin.id'))
    employee = db.relationship('Employee')
    role = db.relationship('Role')

class Employee(db.Model, UserMixin):
    employee_id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(150), db.ForeignKey('role.role_type'))
    first_name = db.Column(db.String(150))
    middle_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    mobile = db.Column(db.Integer)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    role = db.relationship('Role')

class Role(db.Model, UserMixin):
    role_id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.String(150), unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'))

'''