from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)

  db_connection = os.environ['DB_CONNECTION_STRING']
  app.config['SQLALCHEMY_DATABASE_URI'] = db_connection
  
  db.init_app(app)

  from .models import User

  with app.app_context():
    db.create_all()

  @app.route('/')
  def index():
    return 'Hello from Flask!'

  return app
  



  