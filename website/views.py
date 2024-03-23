from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Employee, Role, Gender, Education, Marital, Family, Country, State, City, Photo, Identification, Caddress, Paddress, Weapon, Career, Army
from flask_cors import CORS, cross_origin
from . import db
import os
from PIL import Image
from werkzeug.utils import secure_filename
from . import create_app
import time
from botocore.exceptions import ClientError
import boto3

views = Blueprint('views', __name__)
CORS(views)


@views.route('/display')
@login_required
def display():
  return render_template("display.html", user=current_user)


######## DASHBOARD ########


@views.route('/', methods=['GET', 'POST'])
@login_required
@cross_origin()
def dashboard():
  company_name = request.args.get('company_name', 'Default Company')
  return render_template("dashboard.html", user=current_user)


######## ALL EMPLOYEES ########


@views.route('/employee', methods=['GET', 'POST'])
@login_required
@cross_origin()
def employee():
  return render_template("employee.html", user=current_user)


######## VIEW EMPLOYEE ########


@views.route('/employee_details/<employee_id>', methods=['GET'])
@login_required
@cross_origin()
def employee_details(employee_id):
  employee = Employee.query.filter_by(employee_id=employee_id).first()
  if employee:
    identification = Identification.query.filter_by(
        employee_id=employee.employee_id).first()
    family = Family.query.filter_by(employee_id=employee.employee_id).all()
    caddress = Caddress.query.filter_by(
        employee_id=employee.employee_id).first()
    paddress = Paddress.query.filter_by(
        employee_id=employee.employee_id).first()
    weapons = Weapon.query.filter_by(employee_id=employee.employee_id).all()
    careers = Career.query.filter_by(employee_id=employee.employee_id).all()
    army = Army.query.filter_by(employee_id=employee.employee_id).all()
    photo = Photo.query.filter_by(employee_id=employee.employee_id).first()

    # If photo exists, construct static file path
    static_file_path = None
    if photo:
        static_file_path = f"https://{bucket_name}.s3.amazonaws.com/{photo.stored_file_name}"

      

    return render_template("employee_details.html",
                           employee=employee,
                           identification=identification,
                           family=family,
                           caddress=caddress,
                           paddress=paddress,
                           weapons=weapons,
                           careers=careers,
                           army=army,
                           photo=photo,
                           static_file_path=static_file_path,
                           user=current_user)
  else:
    flash('Employee not found.', category='error')
    return redirect(url_for('views.employee_list'))


######## ADD EMPLOYEE ########


def generate_employee_id(company_code):
  last_employee = Employee.query.filter(
      Employee.employee_id.like(f'{company_code}%')).order_by(
          Employee.employee_id.desc()).first()
  if last_employee:
    last_id_number = int(last_employee.employee_id[len(company_code):])
    new_id_number = last_id_number + 1
  else:
    new_id_number = 1

  return f'{company_code}{new_id_number:06d}'


@views.route('/add_employee', methods=['GET', 'POST'])
@login_required
@cross_origin()
def add_employee():
  if request.method == 'POST':
    company_code = current_user.company_code
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')
    last_name = request.form.get('last_name')
    gender_id = request.form.get('gender')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    role_id = request.form.get('role_id')
    birthdate = request.form.get('birthdate')
    height = request.form.get('height')
    weight = request.form.get('weight')
    education_id = request.form.get('education_id')
    marital_id = request.form.get('marital_id')
    pan = request.form.get('pan')
    aadhar = request.form.get('aadhar')
    voter = request.form.get('voter')
    passport = request.form.get('passport')
    dl = request.form.get('dl')
    caddress_line1 = request.form.get('caddress_line1')
    cstreet = request.form.get('cstreet')
    cpin = request.form.get('cpin')
    cvillage = request.form.get('cvillage')
    ccity_id = request.form.get('ccity_id')
    cstate_id = request.form.get('cstate_id')
    ccountry_id = request.form.get('ccountry_id')
    paddress_line1 = request.form.get('paddress_line1')
    pstreet = request.form.get('pstreet')
    ppin = request.form.get('ppin')
    pvillage = request.form.get('pvillage')
    pcity_id = request.form.get('pcity_id')
    pstate_id = request.form.get('pstate_id')
    pcountry_id = request.form.get('pcountry_id')
    family_names = request.form.getlist('familyName[]')
    family_birthdates = request.form.getlist('familyBirthdate[]')
    family_relations = request.form.getlist('familyRelation[]')
    weapon = request.form.getlist('weapon[]')
    license = request.form.getlist('license[]')
    career_companies = request.form.getlist('careerCompany[]')
    career_joiningdates = request.form.getlist('careerJoiningdate[]')
    career_leavingdates = request.form.getlist('careerLeavingdate[]')
    force = request.form.get('force')
    joining = request.form.get('joining')
    leaving = request.form.get('leaving')

    if not first_name or not last_name or not email or not mobile:
      flash('All fields are required.', category='error')
    else:
      try:
        existing_employee = Employee.query.filter_by(email=email).first()
        if existing_employee:
          flash('Email already exists. Please use a different email address.',
                category='error')
        else:
          employee_id = generate_employee_id(company_code)
          role = Role.query.get(role_id)
          gender = Gender.query.get(gender_id)
          education = Education.query.get(education_id)
          marital = Marital.query.get(marital_id)

          # Create a new Employee instance and add it to the database
          new_employee = Employee(employee_id=employee_id,
                                  first_name=first_name,
                                  middle_name=middle_name,
                                  last_name=last_name,
                                  gender_id=gender_id,
                                  email=email,
                                  mobile=mobile,
                                  user_id=current_user.id,
                                  role=role,
                                  birthdate=birthdate,
                                  height=height,
                                  weight=weight,
                                  education_id=education_id,
                                  marital_id=marital_id)

          db.session.add(new_employee)
          db.session.commit()
          flash('Employee added successfully!', category='success')

          # Add family members
          for name, bdate, relation in zip(family_names, family_birthdates,
                                           family_relations):
            new_family_member = Family(employee_id=new_employee.employee_id,
                                       fullname=name,
                                       birthdate=bdate,
                                       relation=relation)
            db.session.add(new_family_member)

          # Add Carrer
          for company, cjoiningdate, cleavingdate in zip(
              career_companies, career_joiningdates, career_leavingdates):
            new_career = Career(employee_id=new_employee.employee_id,
                                company=company,
                                joiningdate=cjoiningdate,
                                leavingdate=cleavingdate)
            db.session.add(new_career)

          # Add weapon
          for weapon, license in zip(weapon, license):
            new_weapon = Weapon(employee_id=new_employee.employee_id,
                                weapon=weapon,
                                license=license)
            db.session.add(new_weapon)

          # Add Army
          new_army = Army(employee_id=new_employee.employee_id,
                          force=force,
                          joining=joining,
                          leaving=leaving)
          db.session.add(new_army)

          # Add identification details
          new_identification = Identification(
              pan=pan,
              aadhar=aadhar,
              voter=voter,
              passport=passport,
              dl=dl,
              employee_id=new_employee.employee_id)
          db.session.add(new_identification)

          # Add current address
          new_caddress = Caddress(address_line1=caddress_line1,
                                  street=cstreet,
                                  pin=cpin,
                                  village=cvillage,
                                  city_id=ccity_id,
                                  state_id=cstate_id,
                                  country_id=ccountry_id,
                                  employee_id=new_employee.employee_id)
          db.session.add(new_caddress)

          # Add permanent address
          new_paddress = Paddress(address_line1=paddress_line1,
                                  street=pstreet,
                                  pin=ppin,
                                  village=pvillage,
                                  city_id=pcity_id,
                                  state_id=pstate_id,
                                  country_id=pcountry_id,
                                  employee_id=new_employee.employee_id)
          db.session.add(new_paddress)

          db.session.commit()

      except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', category='error')

  # Query roles associated with the current user
  roles = Role.query.filter_by(user_id=current_user.id).all()
  genders = Gender.query.all()
  educations = Education.query.all()
  maritals = Marital.query.all()
  countries = Country.query.all()
  states = State.query.all()
  cities = City.query.all()

  return render_template("add_employee.html",
                         user=current_user,
                         roles=roles,
                         genders=genders,
                         educations=educations,
                         maritals=maritals,
                         countries=countries,
                         states=states,
                         cities=cities)


######## EDIT/UPDATE EMPLOYEE ########


@views.route('/edit_employee/<employee_id>', methods=['GET', 'POST'])
@login_required
@cross_origin()
def edit_employee(employee_id):
  employee = Employee.query.filter_by(employee_id=employee_id).first()
  if employee:
    identification = Identification.query.filter_by(
        employee_id=employee_id).first()
    caddress = Caddress.query.filter_by(employee_id=employee_id).first()
    paddress = Paddress.query.filter_by(employee_id=employee_id).first()
    army = Army.query.filter_by(employee_id=employee_id).first()
    family = Family.query.filter_by(employee_id=employee_id).all()
    careers = Career.query.filter_by(employee_id=employee_id).all()
    weapons = Weapon.query.filter_by(employee_id=employee_id).all()
    photo = Photo.query.filter_by(employee_id=employee_id).first()
    
    # If photo exists, construct static file path
    static_file_path = None
    if photo:
        static_file_path = f"https://{bucket_name}.s3.amazonaws.com/{photo.stored_file_name}"

    
  if not employee:
    flash('Employee not found.', category='error')
    return redirect(url_for('views.employee_list'))

  if request.method == 'POST':
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')
    last_name = request.form.get('last_name')
    gender_id = request.form.get('gender')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    role_id = request.form.get('role_id')
    birthdate = request.form.get('birthdate')
    height = request.form.get('height')
    weight = request.form.get('weight')
    education_id = request.form.get('education')
    marital_id = request.form.get('marital_id')
    pan = request.form.get('pan')
    aadhar = request.form.get('aadhar')
    voter = request.form.get('voter')
    passport = request.form.get('passport')
    dl = request.form.get('dl')
    caddress_line1 = request.form.get('caddress_line1')
    cstreet = request.form.get('cstreet')
    cpin = request.form.get('cpin')
    cvillage = request.form.get('cvillage')
    ccity_id = request.form.get('ccity_id')
    cstate_id = request.form.get('cstate_id')
    ccountry_id = request.form.get('ccountry_id')
    paddress_line1 = request.form.get('paddress_line1')
    pstreet = request.form.get('pstreet')
    ppin = request.form.get('ppin')
    pvillage = request.form.get('pvillage')
    pcity_id = request.form.get('pcity_id')
    pstate_id = request.form.get('pstate_id')
    pcountry_id = request.form.get('pcountry_id')
    family_names = request.form.getlist('familyName[]')
    family_birthdates = request.form.getlist('familyBirthdate[]')
    family_relations = request.form.getlist('familyRelation[]')
    weapon = request.form.getlist('weapon[]')
    license = request.form.getlist('license[]')
    career_companies = request.form.getlist('careerCompany[]')
    career_joiningdates = request.form.getlist('careerJoiningdate[]')
    career_leavingdates = request.form.getlist('careerLeavingdate[]')
    force = request.form.get('force')
    joining = request.form.get('joining')
    leaving = request.form.get('leaving')
    
   

    if not first_name or not last_name or not email or not mobile:
      flash('All fields are required.', category='error')
    else:
      try:

        employee.first_name = first_name
        employee.middle_name = middle_name
        employee.last_name = last_name
        employee.gender_id = gender_id
        employee.email = email
        employee.mobile = mobile
        employee.role_id = role_id
        employee.birthdate = birthdate
        employee.height = height
        employee.weight = weight
        employee.education_id = education_id
        employee.marital_id = marital_id
        identification.pan = pan
        identification.aadhar = aadhar
        identification.voter = voter
        identification.passport = passport
        identification.dl = dl
        caddress.address_line1 = caddress_line1
        caddress.street = cstreet
        caddress.pin = cpin
        caddress.village = cvillage
        caddress.city_id = ccity_id
        caddress.state_id = cstate_id
        caddress.country_id = ccountry_id
        paddress.address_line1 = paddress_line1
        paddress.street = pstreet
        paddress.pin = ppin
        paddress.village = pvillage
        paddress.city_id = pcity_id
        paddress.state_id = pstate_id
        paddress.country_id = pcountry_id
        photo.static_file_path = static_file_path



        # Update existing family members
        for member in family:
          member.fullname = request.form.get(f'family_name_{member.id}')
          member.relation = request.form.get(f'family_relation_{member.id}')
          member.birthdate = request.form.get(f'family_birthdate_{member.id}')

        # Create new family members
        for name, bdate, relation in zip(
            request.form.getlist('familyName[]'),
            request.form.getlist('familyBirthdate[]'),
            request.form.getlist('familyRelation[]')):
          new_family_member = Family(employee_id=employee.employee_id,
                                     fullname=name,
                                     birthdate=bdate,
                                     relation=relation)
          db.session.add(new_family_member)

        # Delete family members
        deleted_member_ids = request.form.getlist('deleted_family_member_ids')
        for member_id in deleted_member_ids:
          member_to_delete = Family.query.get(member_id)
          if member_to_delete:
            db.session.delete(member_to_delete)

        # Update existing weapons
        for weapon in weapons:
          weapon_type = request.form.get(f'weapon_{weapon.id}')
          license_number = request.form.get(f'license_{weapon.id}')
          weapon.weapon = weapon_type
          weapon.license = license_number


        # Delete existing weapons
        deleted_weapon_ids = request.form.getlist('deleted_weapon_ids')
        for weapon_id in deleted_weapon_ids:
            weapon_to_delete = Weapon.query.get(weapon_id)
            if weapon_to_delete:
                db.session.delete(weapon_to_delete)

        # Create new weapons
        new_weapons = []
        new_weapon_types = request.form.getlist('new_weapon[]')
        new_license_numbers = request.form.getlist('new_license[]')

        # Ensure the lengths of both lists are the same
        if len(new_weapon_types) == len(new_license_numbers):
            for weapon_type, license_number in zip(new_weapon_types, new_license_numbers):
                # Only create a new weapon if both the type and license are provided
                if weapon_type:
                    new_weapon = Weapon(employee_id=employee.employee_id,
                                        weapon=weapon_type,
                                        license=license_number)
                    new_weapons.append(new_weapon)
        else:
            flash('Invalid new weapon data.', category='error')

        # Add new weapons to the database
        db.session.add_all(new_weapons)

        # Update career details
        for career in careers:
          career.company = request.form.get(f'career_company_{career.id}')
          career.joiningdate = request.form.get(
              f'career_joiningdate_{career.id}')
          career.leavingdate = request.form.get(
              f'career_leavingdate_{career.id}')

        # Delete existing career entries
        deleted_career_ids = request.form.getlist('deleted_career_ids')
        for career_id in deleted_career_ids:
          career_to_delete = Career.query.get(career_id)
          if career_to_delete:
            db.session.delete(career_to_delete)

        # Create new career entries
        for company, cjoiningdate, cleavingdate in zip(career_companies,
                                                       career_joiningdates,
                                                       career_leavingdates):
          new_career = Career(employee_id=employee.employee_id,
                              company=company,
                              joiningdate=cjoiningdate,
                              leavingdate=cleavingdate)
          db.session.add(new_career)

        # Update Army details
        if army:
          army.force = force
          army.joining = joining
          army.leaving = leaving
        else:
          new_army = Army(force=force,
                          joining=joining,
                          leaving=leaving,
                          employee_id=employee_id)
          db.session.add(new_army)

        db.session.commit()
        flash('Employee information updated successfully!', category='success')
      except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', category='error')

        db.session.commit()
        flash('Employee details updated successfully!', category='success')
        return redirect(
            url_for('views.employee_details', employee_id=employee_id))

  genders = Gender.query.all()
  educations = Education.query.all()
  maritals = Marital.query.all()
  countries = Country.query.all()
  states = State.query.all()
  cities = City.query.all()  
  roles = Role.query.filter_by(user_id=current_user.id).all()

  return render_template("edit_employee.html",
                         employee=employee,
                         identification=identification,
                         family=family,
                         weapons=weapons,
                         careers=careers,
                         army=army,
                         caddress=caddress,
                         paddress=paddress,
                         genders=genders,
                         educations=educations,
                         maritals=maritals,
                         countries=countries,
                         states=states,
                         cities=cities,
                         roles=roles,
                         photo=photo,
                         current_user=current_user,
                         static_file_path=static_file_path,
                         user=current_user)


######## ADD PHOTO ########

s3 = boto3.client('s3',
                  aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                  region_name='ap-south-1'
                  )
bucket_name = 'securityemployee'

ALLOWED_FILE_TYPES = {'png', 'jpg', 'jpeg'}

def get_file_type(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() 
  
@views.route('/upload/<employee_id>', methods=['POST'])
@login_required
def upload(employee_id):
    # Fetch the employee based on the provided employee_id
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    photo = Photo.query.filter_by(employee_id=employee_id).first()

    if not employee:
      flash("Employee not found.")
      return redirect(url_for('some_redirect_route'))

    if 'file' in request.files:
      file = request.files['file']
      if file.filename != '':
          # Check if the file type is allowed
          if get_file_type(file.filename) not in ALLOWED_FILE_TYPES:
              flash("File type not allowed.")
              return redirect(url_for('some_redirect_route'))

          # Generate unique file name and employee folder path
          company_code = current_user.company_code
          employee_folder = f"{company_code}/{employee_id}/"
          unique_filename = f"uploaded_{int(time.time())}{os.path.splitext(file.filename)[1]}"
          file_path = os.path.join(employee_folder, secure_filename(unique_filename))

          # Delete the existing photo from S3 and database if exists
          if photo:
              try:
                  s3.delete_object(Bucket=bucket_name, Key=photo.stored_file_name)
              except ClientError as e:
                  flash("An error occurred while deleting the existing photo from S3.")
                  return redirect(url_for('some_redirect_route'))

              db.session.delete(photo)
              db.session.commit()

          # Upload the file to S3
          try:
              s3.upload_fileobj(file, bucket_name, file_path)

              # Save the unique file name in the database
              photo = Photo(stored_file_name=file_path, employee_id=employee_id)
              db.session.add(photo)
              db.session.commit()

              # Generate pre-signed URL for the uploaded photo
              presigned_url = s3.generate_presigned_url(
                  'get_object',
                  Params={'Bucket': bucket_name, 'Key': file_path},
                  ExpiresIn=31536000  # URL expires in 1 hour, adjust as needed
              )

              # Construct the URL for serving static files
              static_file_path = f"https://{bucket_name}.s3.amazonaws.com/{file_path}"

              # Redirect back to edit_employee page with presigned URL and static file path
              return redirect(url_for('views.edit_employee', employee_id=employee_id,
                                       presigned_url=presigned_url, static_file_path=static_file_path))

              
          except ClientError as e:
              if e.response['Error']['Code'] == 'NoCredentialsError':
                  flash("Credentials not available.")
              else:
                  flash("An error occurred while uploading the file.")
              return redirect(url_for('some_redirect_route'))

    # If the file upload fails or if no file was uploaded, render the edit_employee template
    return render_template('edit_employee.html',
                         employee=employee,
                           photo=photo,
                         user=current_user)


def get_presigned_file_url(stored_file_name):
    if not presigned_url or not provided_file_name:
        return
    return presigned_url.split('?')[0] + '?' + urlencode({
        'response-content-disposition': f'attachment; filename="{provided_file_name}"'
    })


'''
@views.route('/upload/<employee_id>', methods=['POST'])
@login_required
def upload(employee_id):
    # Fetch the employee based on the provided employee_id
    employee = Employee.query.filter_by(employee_id=employee_id).all()
    identification = Identification.query.filter_by(
        employee_id=employee_id).first()
    caddress = Caddress.query.filter_by(employee_id=employee_id).first()
    family = Family.query.filter_by(employee_id=employee_id).all()
    weapons = Weapon.query.filter_by(employee_id=employee_id).all()
    careers = Career.query.filter_by(employee_id=employee_id).all()
    army = Army.query.filter_by(employee_id=employee_id).first()
    paddress = Paddress.query.filter_by(employee_id=employee_id).first()
    photo = Photo.query.filter_by(employee_id=employee_id).first()

    if not employee:
        flash("Employee not found.")
        return redirect(url_for('some_redirect_route'))
          

    existing_photo = Photo.query.filter_by(employee_id=employee_id).first()
    if existing_photo:
        # Delete the existing photo file from the file system
        existing_photo_path = os.path.join('website', 'static', 'media', existing_photo.path)
        if os.path.exists(existing_photo_path):
            os.remove(existing_photo_path)

        # Delete the existing photo record from the database
        db.session.delete(existing_photo)
        db.session.commit()

    if 'file' in request.files:
      file = request.files['file']
      if file.filename != '':
          company_code = current_user.company_code

          company_folder = os.path.join('static', 'media', company_code)
          os.makedirs(os.path.join('website', company_folder), exist_ok=True)

          employee_folder = os.path.join(company_folder, employee_id)
          os.makedirs(os.path.join('website', employee_folder), exist_ok=True)

          unique_filename = f"uploaded_{int(time.time())}{os.path.splitext(file.filename)[1]}"
          file_path = os.path.join(employee_folder, unique_filename)

          file.save(os.path.join('website', file_path))

          # Create a new Photo object for the database
          photo = Photo(path=os.path.join(company_code, employee_id, unique_filename),
                        employee_id=employee_id)

          # Add the new photo to the database
          db.session.add(photo)
          db.session.commit()

          # Construct the URL for serving static files
          static_file_path = os.path.join('media', company_code, employee_id, unique_filename)

          return render_template('edit_employee.html',
                                 employee=employee,
                                 caddress=caddress,
                                 identification=identification,
                                 family=family,
                                 weapons=weapons,
                                 careers=careers,
                                 paddress=paddress,
                                 army=army,
                                 user=current_user,
                                 photo=photo,
                                 file_path=static_file_path)
                                 
'''
######## ADD ROLES ########


@views.route('/role', methods=['GET', 'POST'])
@login_required
@cross_origin()
def role():
  if request.method == 'POST':
    role_name = request.form.get('role_name')
    description = request.form.get('description')

    if not role_name:
      flash('Role name is required.', category='error')
    else:
      existing_role = Role.query.filter_by(role=role_name,
                                           user_id=current_user.id).first()

      if existing_role:
        flash('Role type already exists.', category='error')
      else:
        new_role = Role(role=role_name,
                        description=description,
                        user_id=current_user.id)
        db.session.add(new_role)
        db.session.commit()
        flash('Role added successfully!', category='success')

  roles = Role.query.filter_by(user_id=current_user.id).all()
  return render_template("role.html", user=current_user, roles=roles)


######## EDIT ROLES ########


@views.route('/edit_role/<int:role_id>', methods=['GET', 'POST'])
@login_required
@cross_origin()
def edit_role(role_id):
  role = Role.query.get_or_404(role_id)

  if request.method == 'POST':
    role_name = request.form.get('role_name')
    description = request.form.get('description')

    if not role_name:
      flash('Role name is required.', category='error')
    else:
      existing_role = Role.query.filter_by(role=role_name,
                                           user_id=current_user.id).first()

      if existing_role and existing_role.id != role.id:
        flash('Role already exists. Please select another name.',
              category='error')
      else:
        role.role = role_name
        role.description = description
        db.session.commit()
        flash('Role updated successfully!', category='success')
        return redirect(url_for('views.role'))

  return render_template("edit_role.html", user=current_user, role=role)


@views.route('/add_location', methods=['GET', 'POST'])
def add_location():
  if request.method == 'POST':
    location_type = request.form.get('location_type')
    name = request.form.get('name')
    parent_id = request.form.get('parent_id')

    if not name:
      flash('Name is required.', category='error')
    else:
      try:
        if location_type == 'country':
          new_location = Country(country=name)
        elif location_type == 'state':
          new_location = State(state=name, country_id=parent_id)
        elif location_type == 'city':
          new_location = City(city=name, state_id=parent_id)

        db.session.add(new_location)
        db.session.commit()
        flash('Location added successfully!', category='success')
      except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', category='error')

  countries = Country.query.all()
  states = State.query.all()
  cities = City.query.all()

  return render_template("add_location.html",
                         countries=countries,
                         states=states,
                         cities=cities,
                         user=current_user)


# Route for displaying employee data
@views.route('/display_employee', methods=['GET'])
def display_employee():
  # Retrieve employee data from the database
  employees = Employee.query.all()

  return render_template('display_employee.html', employees=employees)
