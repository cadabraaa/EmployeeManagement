from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Employee, Role, Gender
from flask_cors import CORS, cross_origin
from . import db

views = Blueprint('views', __name__)
CORS(views)

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
        gender_id = request.form.get('gender')  # Change to gender_id to match the column name
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        role_id = request.form.get('role_id')

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

                    # Create a new Employee instance and add it to the database
                    new_employee = Employee(
                        employee_id=employee_id,
                        first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        gender_id=gender_id,  # Assign the gender_id
                        email=email,
                        mobile=mobile,
                        user_id=current_user.id,
                        role=role
                    )

                    db.session.add(new_employee)
                    db.session.commit()
                    flash('Employee added successfully!', category='success')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', category='error')

    # Query roles associated with the current user
    roles = Role.query.filter_by(user_id=current_user.id).all()
    genders = Gender.query.all()  # Query all genders

    return render_template("add_employee.html", user=current_user, roles=roles, genders=genders)

'''
@views.route('/add_employee', methods=['GET', 'POST'])
@login_required
@cross_origin()
def add_employee():
    if request.method == 'POST':
        company_code = current_user.company_code
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        role_id = request.form.get('role_id')

        if not first_name or not last_name or not email or not mobile:
            flash('All fields are required.', category='error')
        else:
            existing_employee = Employee.query.filter_by(email=email).first()
            if existing_employee:
                flash('Email already exists. Please use a different email address.', category='error')
            else:
                employee_id = generate_employee_id(company_code)
                print(f"Generated employee_id: {employee_id}")
                role = Role.query.get(role_id)
                new_employee = Employee(
                    employee_id=employee_id,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    gender=gender,
                    email=email,
                    mobile=mobile,
                    user_id=current_user.id,
                    role=role
                )

                db.session.add(new_employee)
                db.session.commit()
                flash('Employee added successfully!', category='success')

    roles = Role.query.filter_by(user_id=current_user.id).all()
    print(roles)
    return render_template("add_employee.html", user=current_user, roles=roles, gender=genders)
'''


######## ADD ROLES ########

@views.route('/role', methods=['GET', 'POST'])
@login_required
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

