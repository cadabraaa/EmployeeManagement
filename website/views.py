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


views = Blueprint('views', __name__)
CORS(views)

@views.route('/display')
@login_required
def display():
  return render_template("display.html",user=current_user)

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

######## VIEW Details ########

@views.route('/employee_details/<employee_id>', methods=['GET'])
@login_required
def employee_details(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if employee:
        return render_template("employee_details.html", employee=employee,user=current_user)
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
        family_names = request.form.getlist('familyName[]')
        family_birthdates = request.form.getlist('familyBirthdate[]')
        family_relations = request.form.getlist('familyRelation[]')
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
                    flash('Email already exists. Please use a different email address.', category='error')
                else:
                    employee_id = generate_employee_id(company_code)
                    role = Role.query.get(role_id)
                    gender = Gender.query.get(gender_id)
                    education = Education.query.get(education_id)
                    marital = Marital.query.get(marital_id)

                    # Create a new Employee instance and add it to the database
                    new_employee = Employee(
                        employee_id=employee_id,
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
                        marital_id=marital_id
                    )

                    db.session.add(new_employee)
                    db.session.commit()
                    flash('Employee added successfully!', category='success')

                    # Add family members
                    for name, bdate, relation in zip(family_names, family_birthdates, family_relations):
                        new_family_member = Family(
                            employee_id=new_employee.employee_id,
                            fullname=name,
                            birthdate=bdate,
                            relation=relation
                        )
                        db.session.add(new_family_member)

                    # Add Carrer
                    for company, cjoiningdate, cleavingdate in zip(career_companies, career_joiningdates, career_leavingdates):
                        new_career = Career(
                            employee_id=new_employee.employee_id,
                            company=company,
                            joiningdate=cjoiningdate,
                            leavingdate=cleavingdate
                        )
                        db.session.add(new_career)

                    # Add Army
                    new_army = Army(
                        employee_id=new_employee.employee_id,
                        force=force,
                        joining=joining,
                        leaving=leaving
                    )
                    db.session.add(new_army)

                    # Add weapon
                    for weapon, license in zip(weapon, license):
                        new_weapon = Weapon(
                          employee_id=new_employee.employee_id,
                          weapon=weapon,
                          license=license
                        )
                        db.session.add(new_weapon)

                    # Add identification details
                    new_identification = Identification(
                        pan=pan,
                        aadhar=aadhar,
                        voter=voter,
                        passport=passport,
                        dl=dl,
                        employee_id=new_employee.employee_id
                    )
                    db.session.add(new_identification)

                    
                    # Add current address
                    new_caddress = Caddress(
                        address_line1=caddress_line1,
                        street=cstreet,
                        pin=cpin,
                        village=cvillage,
                        city_id=ccity_id,
                        state_id=cstate_id,
                        country_id=ccountry_id,
                        employee_id=new_employee.employee_id
                    )
                    db.session.add(new_caddress)

                    # Add permanent address
                    new_paddress = Paddress(
                        address_line1=paddress_line1,
                        street=pstreet,
                        pin=ppin,
                        village=pvillage,
                        city_id=pcity_id,
                        state_id=pstate_id,
                        country_id=pcountry_id,
                        employee_id=new_employee.employee_id
                    )
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

    return render_template(
        "add_employee.html", 
        user=current_user, 
        roles=roles, 
        genders=genders, 
        educations=educations, 
        maritals=maritals,
        countries=countries,
        states=states,
        cities=cities
    )






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
            existing_role = Role.query.filter_by(role=role_name, user_id=current_user.id).first()

            if existing_role:
                flash('Role type already exists.', category='error')
            else:
                new_role = Role(role=role_name, description=description, user_id=current_user.id)
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
            existing_role = Role.query.filter_by(role=role_name, user_id=current_user.id).first()

            if existing_role and existing_role.id != role.id:
                flash('Role already exists. Please select another name.', category='error')
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

    return render_template("add_location.html", countries=countries, states=states, cities=cities, user=current_user)



# Route for displaying employee data
@views.route('/display_employee', methods=['GET'])
def display_employee():
    # Retrieve employee data from the database
    employees = Employee.query.all()

    return render_template('display_employee.html', employees=employees)

