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
    email = db.Column(db.String(150), unique=True)
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
    

class Gender(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  gender = db.Column(db.String(50), unique=True)
  employees = db.relationship('Employee', backref='gender', lazy=True)

class Role(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  role = db.Column(db.String(50), unique=True)
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

class Family(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.String(15), db.ForeignKey('employee.employee_id'))
  fullname = db.Column(db.String(150))
  relation = db.Column(db.String(50))
  birthdate = db.Column(db.Date)
  



class Country(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  country = db.Column(db.String(150), unique=True)
  

class State(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  state = db.Column(db.String(150), unique=True)
  country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
  country = db.relationship('Country', backref='states')
  cities = db.relationship('City', backref='state', lazy=True)
 

class City(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  city = db.Column(db.String(150), unique=True)
  state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
  
  
