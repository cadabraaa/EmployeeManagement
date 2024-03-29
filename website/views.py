from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response, render_template_string
from flask_login import login_required, current_user
from .models import Employee, Role, Gender, Education, Marital, Family, Country, State, City, Photo, Identification, Caddress, Paddress, Weapon, Career, Army, Documents, Bankdetails
from flask_cors import CORS, cross_origin
from . import db
import os
from PIL import Image
from werkzeug.utils import secure_filename
from . import create_app
import time
from botocore.exceptions import ClientError
import botocore
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
    bankdetails = Bankdetails.query.filter_by(
        employee_id=employee.employee_id)

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
                           bankdetails=bankdetails,
                           photo=photo,
                           static_file_path=static_file_path,
                           user=current_user)
  else:
    flash('Employee not found.', category='error')
    return redirect(url_for('views.employee_list'))

  
####### EMPLOYEE PDF ########

@views.route('/employee_pdf/<employee_id>', methods=['GET','POST'])
@login_required
@cross_origin()
def employee_pdf(employee_id):
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
    bankdetails = Bankdetails.query.filter_by(
        employee_id=employee.employee_id)

    # If photo exists, construct static file path
    static_file_path = None
    if photo:
        static_file_path = f"https://{bucket_name}.s3.amazonaws.com/{photo.stored_file_name}"


    return render_template("employee_pdf.html",
                           employee=employee,
                           identification=identification,
                           family=family,
                           caddress=caddress,
                           paddress=paddress,
                           weapons=weapons,
                           careers=careers,
                           army=army,
                           bankdetails=bankdetails,
                           photo=photo,
                           static_file_path=static_file_path,
                           user=current_user)

@views.route('/employeeform/<employee_id>', methods=['GET','POST'])
@login_required
@cross_origin()
def employeeform(employee_id):
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
    bankdetails = Bankdetails.query.filter_by(
        employee_id=employee.employee_id)

    # If photo exists, construct static file path
    static_file_path = None
    if photo:
        static_file_path = f"https://{bucket_name}.s3.amazonaws.com/{photo.stored_file_name}"


    return render_template("employeeform.html",
                           employee=employee,
                           identification=identification,
                           family=family,
                           caddress=caddress,
                           paddress=paddress,
                           weapons=weapons,
                           careers=careers,
                           army=army,
                           bankdetails=bankdetails,
                           photo=photo,
                           static_file_path=static_file_path,
                           user=current_user)



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
    caddress_line2 = request.form.get('caddress_line2')
    cpin = request.form.get('cpin')
    ccity_id = request.form.get('ccity_id')
    cstate_id = request.form.get('cstate_id')
    ccountry_id = request.form.get('ccountry_id')
    paddress_line1 = request.form.get('paddress_line1')
    paddress_line2 = request.form.get('paddress_line2')
    ppin = request.form.get('ppin')
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
    bankname = request.form.getlist('bankname[]')
    branch = request.form.getlist('branch[]')
    account = request.form.getlist('account[]')
    ifsc = request.form.getlist('ifsc[]')

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

          # Add Bank Details
          for bankname, branch, account, ifsc in zip(bankname, branch, account, ifsc):
              new_bankdetails = Bankdetails(employee_id=new_employee.employee_id,
                                            bankname=bankname,
                                            branch=branch,
                                            account=account,
                                            ifsc=ifsc)
              db.session.add(new_bankdetails)

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
                                  address_line2=caddress_line2,
                                  pin=cpin,
                                  city_id=ccity_id,
                                  state_id=cstate_id,
                                  country_id=ccountry_id,
                                  employee_id=new_employee.employee_id)
          db.session.add(new_caddress)

          # Add permanent address
          new_paddress = Paddress(address_line1=paddress_line1,
                                  address_line2=paddress_line2,
                                  pin=ppin,
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
    bankdetails = Bankdetails.query.filter_by(employee_id=employee_id).all()

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
    role_id = request.form.get('role')
    birthdate = request.form.get('birthdate')
    height = request.form.get('height')
    weight = request.form.get('weight')
    education_id = request.form.get('education')
    marital_id = request.form.get('marital')
    pan = request.form.get('pan')
    aadhar = request.form.get('aadhar')
    voter = request.form.get('voter')
    passport = request.form.get('passport')
    dl = request.form.get('dl')
    caddress_line1 = request.form.get('caddress_line1')
    caddress_line2 = request.form.get('caddress_line2')
    cpin = request.form.get('cpin')
    ccity_id = request.form.get('ccity_id')
    cstate_id = request.form.get('cstate_id')
    ccountry_id = request.form.get('ccountry_id')
    paddress_line1 = request.form.get('paddress_line1')
    paddress_line2 = request.form.get('paddress_line2')
    ppin = request.form.get('ppin')
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
    bankname = request.form.getlist('bankname[]')
    branch = request.form.getlist('branch[]')
    account = request.form.getlist('account[]')
    ifsc = request.form.getlist('ifsc[]')


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
        caddress.address_line2 = caddress_line2
        caddress.pin = cpin
        caddress.city_id = ccity_id
        caddress.state_id = cstate_id
        caddress.country_id = ccountry_id
        paddress.address_line1 = paddress_line1
        paddress.address_line2 = paddress_line2
        paddress.pin = ppin
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


        # Update existing bank details
        for bank in bankdetails:
          bank.bankname = request.form.get(f'bankdetails_bankname{bank.id}')
          bank.branch = request.form.get(f'bankdetails_branch{bank.id}')
          bank.account = request.form.get(f'bankdetails_account{bank.id}')
          bank.ifsc = request.form.get(f'bankdetails_ifsc{bank.id}')


        #  Create new Bank Details
        for bankname, branch, account, ifsc in zip(bankname, branch, account, ifsc):
            new_bankdetails = Bankdetails(employee_id=employee.employee_id,
                                          bankname=bankname,
                                          branch=branch,
                                          account=account,
                                          ifsc=ifsc)
            db.session.add(new_bankdetails)

        # Delete bank details
        deleted_bankdetail_ids = request.form.getlist('deleted_bankdetail_ids')
        for bankdetail_id in deleted_bankdetail_ids:
          bankdetail_to_delete = Bankdetails.query.get(bankdetail_id)
          if bankdetail_to_delete:
            db.session.delete(bankdetail_to_delete)

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
                         bankdetails=bankdetails,
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

ALLOWED_FILE_TYPES = {'gif','png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}

def get_file_type(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() 
  
@views.route('/upload/<employee_id>', methods=['POST'])
@login_required
@cross_origin()
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
              static_file_path = None
              if photo:
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
    return redirect(url_for('views.edit_employee', employee=employee, photo=photo, static_file_path=static_file_path))

######## ADD DOCUMENTS ########

@views.route('/view_documents/<employee_id>', methods=['GET', 'POST'])
@login_required
@cross_origin()
def view_documents(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        flash("Employee not found.")
        return redirect(url_for('employee'))

    documents = Documents.query.filter_by(employee_id=employee_id).all()

    document_data = []
    presigned_urls = {}
    for document in documents:
        document_entry = {'id': document.id, 'document_name': document.document_name}
        document_data.append(document_entry)

        try:
            company_code = current_user.company_code
            employee_folder = f"{company_code}/{employee_id}/"
            file_path = os.path.join(employee_folder, document.document_name)

            url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name, 'Key': file_path},
                                            ExpiresIn=3600)  # URL expires in 1 hour, adjust as needed
            presigned_urls[document.id] = url
        except botocore.exceptions.ClientError as e:
            flash(f"An error occurred while generating pre-signed URL for document ID {document.id}: {e}")

    static_urls = []
    for document in documents:
        if document.document_path:
            url = f"https://{bucket_name}.s3.amazonaws.com/{document.document_path}"
            static_urls.append(url)
        else:
            flash(f"Document filepath is empty for document ID {document.id}. Skipping URL generation.")

    return render_template('view_documents.html',
                           employee=employee,
                           documents=documents,
                           static_urls=static_urls,
                           presigned_urls=presigned_urls,
                           user=current_user)
  

@views.route('/documents/<employee_id>', methods=['GET', 'POST'])
@login_required
@cross_origin()
def documents(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        flash("Employee not found.")
        return redirect(url_for('employee'))

    documents = Documents.query.filter_by(employee_id=employee_id).all()


    document_data = []
    presigned_urls = {}
    for document in documents:
        document_entry = {'id': document.id, 'document_name': document.document_name}
        document_data.append(document_entry)

        try:
            company_code = current_user.company_code
            employee_folder = f"{company_code}/{employee_id}/"
            file_path = os.path.join(employee_folder, document.document_name)

            url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name, 'Key': file_path},
                                            ExpiresIn=3600)  # URL expires in 1 hour, adjust as needed
            presigned_urls[document.id] = url
        except botocore.exceptions.ClientError as e:
            flash(f"An error occurred while generating pre-signed URL for document ID {document.id}: {e}")

    static_urls = []
    for document in documents:
        if document.document_path:
            url = f"https://{bucket_name}.s3.amazonaws.com/{document.document_path}"
            static_urls.append(url)
        else:
            flash(f"Document filepath is empty for document ID {document.id}. Skipping URL generation.")

    return render_template('documents.html',
                           employee=employee,
                           documents=documents,
                           static_urls=static_urls,
                           presigned_urls=presigned_urls,
                           user=current_user)




@views.route('/upload_documents/<employee_id>', methods=['POST'])
@login_required
def upload_documents(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()

    if not employee:
        flash("Employee not found.")
        return redirect(url_for('some_redirect_route'))

    if 'file' in request.files:
        file = request.files['file']
        filename = request.form.get('filename', file.filename)

        if file.filename != '':
          # Check if the file type is allowed
          if get_file_type(file.filename) not in ALLOWED_FILE_TYPES:
              flash("File type not allowed.")
              return redirect(url_for('some_redirect_route'))

          # Generate unique file name and handle duplicates
          original_filename = filename
          index = 1
          while True:
              # Check if the filename already exists
              existing_document = Documents.query.filter_by(employee_id=employee_id, document_name=filename).first()
              if not existing_document:
                  break
              # If the filename exists, append a suffix
              filename = f"{original_filename} ({index})"
              index += 1

          # Generate unique file name and employee folder path
          company_code = current_user.company_code
          employee_folder = f"{company_code}/{employee_id}/"
          unique_filename = f"{filename}.{get_file_type(file.filename)}"
          file_path = os.path.join(employee_folder, unique_filename)

          # Check if the company folder and employee folder exist, if not create them
          try:
              s3.head_object(Bucket=bucket_name, Key=employee_folder)
          except ClientError as e:
              if e.response['Error']['Code'] == '404':
                  # Create company folder
                  s3.put_object(Bucket=bucket_name, Key=company_code+'/')
                  # Create employee folder
                  s3.put_object(Bucket=bucket_name, Key=employee_folder)
              else:
                  flash("An error occurred while checking folder existence.")
                  return redirect(url_for('views.documents', employee_id=employee_id))

          # Upload the file to S3
          try:
              s3.upload_fileobj(file, bucket_name, file_path)

              # Save document details to the database
              document = Documents(employee_id=employee_id,
                                   document_type=file.content_type,
                                   document_name=filename,
                                   document_path=file_path)
              db.session.add(document)
              db.session.commit()

              # Flash success message
              flash("File uploaded successfully!", category="success")
              # Redirect to a GET route after successful upload
              return redirect(url_for('views.documents', employee_id=employee_id))

          except ClientError as e:
              flash("An error occurred while uploading the file.")
              return redirect(url_for('documents'))

    # Handling document deletion
    document_id_to_delete = request.form.get('delete_document')
    if document_id_to_delete:
        document_to_delete = Documents.query.get(document_id_to_delete)
        if document_to_delete:
            # Delete the document from S3
            try:
                s3.delete_object(Bucket=bucket_name, Key=document_to_delete.document_path)
            except ClientError as e:
                flash(f"An error occurred while deleting the document from S3: {e}")
            # Delete the document from the database
            db.session.delete(document_to_delete)
            db.session.commit()
            flash("Document deleted successfully.")


    # Fetch all documents for the employee
    documents = Documents.query.filter_by(employee_id=employee_id).all()

    # Generate pre-signed URLs for documents
    presigned_urls = {}
    for document in documents:
        if document.document_path:
            try:
                url = s3.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name, 'Key': document.document_path},
                                                ExpiresIn=31536000)  # URL expires in 1 hour, adjust as needed
                presigned_urls[document.id] = url
            except ClientError as e:
                flash(f"An error occurred while generating pre-signed URL for document ID {document.id}: {e}")
        else:
            flash(f"Document path is empty for document ID {document.id}. Skipping URL generation.")

    static_urls = []
    for document in documents:
        if document.document_path:
            url = f"https://{bucket_name}.s3.amazonaws.com/{document.document_path}"
            static_urls.append(url)
        else:
            flash(f"Document filepath is empty for document ID {document.id}. Skipping URL generation.")
    

    return render_template('documents.html',
                           employee=employee,
                           documents=documents,
                           presigned_urls=presigned_urls,
                           static_urls=static_urls,
                           user=current_user)




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


###### ID CARD ######

@views.route('/idcard', methods=['GET', 'POST'])
@login_required
@cross_origin()
def idcard():
    employee_id = request.args.get('employee_id')  # Assuming you're passing employee_id as a query parameter
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
        bankdetails = Bankdetails.query.filter_by(
            employee_id=employee.employee_id)

        # If photo exists, construct static file path
        static_file_path = None
        if photo:
            static_file_path = f"https://{bucket_name}.s3.amazonaws.com/{photo.stored_file_name}"

        return render_template("idcard.html",
                               employee_id=employee_id,
                               employee=employee,
                               identification=identification,
                               family=family,
                               caddress=caddress,
                               paddress=paddress,
                               weapons=weapons,
                               careers=careers,
                               army=army,
                               bankdetails=bankdetails,
                               photo=photo,
                               static_file_path=static_file_path,
                               user=current_user)
    else:
        flash('Employee not found.', category='error')
        return redirect(url_for('views.employee_list'))