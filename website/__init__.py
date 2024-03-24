from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from flask_migrate import Migrate
from flask_cors import CORS
import boto3


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
  

    app.config['SECRET_KEY'] = 'secret_key'
    db_connection = os.environ['DB_CONNECTION_STRING']
    app.config['SQLALCHEMY_DATABASE_URI'] = db_connection

    client = boto3.client('s3',
                        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                        region_name=os.environ['AWS_REGION']
                        )
    response = client.list_buckets()
    for bucket in response['Buckets']:
        print(bucket['Name'])
  
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Employee, Role, Gender, Education, Marital, Family, Country, State, City, Photo, Identification, Caddress, Paddress, Weapon, Career, Army, Documents

    with app.app_context():
      db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
      return User.query.get(int(id))

    return app


  