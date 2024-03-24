from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import BigInteger


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
    email = db.Column(db.String(150))
    mobile = db.Column(BigInteger)
    birthdate = db.Column(db.Date)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'))
    education_id = db.Column(db.Integer, db.ForeignKey('education.id'))
    marital_id = db.Column(db.Integer, db.ForeignKey('marital.id'))
    families = db.relationship('Family', backref='employee', lazy=True)
    Identification = db.relationship('Identification', backref='employee', lazy=True)
    caddress = db.relationship('Caddress', backref='employee', uselist=False)
    paddress = db.relationship('Paddress', backref='employee', uselist=False)
    weapons = db.relationship('Weapon', backref='employee', lazy=True)
    careers = db.relationship('Career', backref='employee', lazy=True)
    army = db.relationship('Army', backref='employee', lazy=True)
    photo = db.relationship('Photo', backref='employee', lazy=True)
    documents = db.relationship('Documents', backref='employee', lazy=True)


class Gender(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  gender = db.Column(db.String(50), unique=True)
  employees = db.relationship('Employee', backref='gender', lazy=True)

class Role(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  role = db.Column(db.String(50))
  description = db.Column(db.String(255))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  employees = db.relationship('Employee', backref='role', lazy=True)
  

class Education(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  education = db.Column(db.String(50), unique=True)
  employees = db.relationship('Employee', backref='education', lazy=True)

class Marital(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  marital = db.Column(db.String(50), unique=True)
  employees = db.relationship('Employee', backref='marital', lazy=True)

class Photo(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  stored_file_name = db.Column(db.String(255))
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  

class Identification(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  pan = db.Column(db.String(255))
  aadhar = db.Column(db.String(255))
  voter = db.Column(db.String(255))
  dl = db.Column(db.String(255))
  passport = db.Column(db.String(255))
  employee_id = db.Column(db.String(50), db.ForeignKey('employee.employee_id'))
  
class Family(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  fullname = db.Column(db.String(150))
  relation = db.Column(db.String(50))
  birthdate = db.Column(db.Date)

class Documents(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  document_type = db.Column(db.String(50))
  document_name = db.Column(db.String(255))
  document_path = db.Column(db.String(255))
  
class Weapon(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  weapon = db.Column(db.String(150))
  license = db.Column(db.String(150))

class Career(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  company = db.Column(db.String(150))
  joiningdate = db.Column(db.Date)
  leavingdate = db.Column(db.Date)

class Army(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  force = db.Column(db.String(150))
  joining = db.Column(db.Date)
  leaving = db.Column(db.Date)


class Caddress(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  address_line1 = db.Column(db.String(255))
  street = db.Column(db.String(100))
  pin = db.Column(db.BigInteger)
  village = db.Column(db.String(100))
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
  state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
  country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
  city = db.relationship('City', backref='caddress')
  state = db.relationship('State', backref='caddress')
  country = db.relationship('Country', backref='caddress')
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))

class Paddress(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  address_line1 = db.Column(db.String(255))
  street = db.Column(db.String(100))
  pin = db.Column(db.BigInteger)
  village = db.Column(db.String(100))
  city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
  state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
  country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
  city = db.relationship('City', backref='paddress')
  state = db.relationship('State', backref='paddress')
  country = db.relationship('Country', backref='paddress')
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))


class Country(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  country = db.Column(db.String(150), unique=True)
  states = db.relationship('State', backref='country')

class State(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  state = db.Column(db.String(150), unique=True)
  country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
  cities = db.relationship('City', backref='state', lazy=True)

class City(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  city = db.Column(db.String(150), unique=True)
  state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
  
  
