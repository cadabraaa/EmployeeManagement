from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(150))
  middle_name = db.Column(db.String(150))
  first_name = db.Column(db.String(150))
  ro = db.Column(db.String(150))
  email = db.Column(db.String(150), unique=True)
  password = db.Column(db.String(150))
  notes = db.relationship('Note')