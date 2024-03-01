from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




'''
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