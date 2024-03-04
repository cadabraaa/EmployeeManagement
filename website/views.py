from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Employee, Role
from . import db

views = Blueprint('views', __name__)

def generate_employee_id(company_code):
    last_employee = Employee.query.filter(Employee.employee_id.like(f'{company_code}%')).order_by(Employee.employee_id.desc()).first()
    if last_employee:
        last_id_number = int(last_employee.employee_id[len(company_code):])
        new_id_number = last_id_number + 1
    else:
        new_id_number = 1
    
    return f'{company_code}{new_id_number:06d}'


@views.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
  company_name = request.args.get('company_name', 'Default Company') 
  return render_template("dashboard.html", user=current_user)


@views.route('/employee', methods=['GET', 'POST'])
@login_required
def employee():
  return render_template("employee.html", user=current_user)


@views.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
      company_code = current_user.company_code 
      first_name = request.form.get('first_name')
      middle_name = request.form.get('middle_name')
      last_name = request.form.get('last_name')
      email = request.form.get('email')
      mobile = request.form.get('mobile')
      role_id = request.form.get('role_id')

      if not first_name or not last_name or not email or not mobile:
          flash('All fields are required.', category='error')
      else:
          employee_id = generate_employee_id(company_code)
          print(f"Generated employee_id: {employee_id}")
          new_employee = Employee(
              employee_id=employee_id,
              first_name=first_name,
              middle_name=middle_name,
              last_name=last_name,
              email=email,
              mobile=mobile,
              user_id=current_user.id,
              role_id=role_id  
          )
          db.session.add(new_employee)
          db.session.commit()
          flash('Employee added successfully!', category='success')

    roles = Role.query.filter_by(user_id=current_user.id).all()
    return render_template("add_employee.html", user=current_user, roles=roles)


@views.route('/role', methods=['GET', 'POST'])
@login_required
def role():
    if request.method == 'POST':
        role_name = request.form.get('role_name')
        description = request.form.get('description')

        if not role_name:
            flash('Role name is required.', category='error')
        else:
            existing_role = Role.query.filter_by(role=role_name).first()

            if existing_role:
                flash('Role type already exists.', category='error')
            else:
                new_role = Role(role=role_name, description=description)
                db.session.add(new_role)
                db.session.commit()
                flash('Role added successfully!', category='success')

    roles = Role.query.all()
    return render_template("role.html", user=current_user, roles=roles)