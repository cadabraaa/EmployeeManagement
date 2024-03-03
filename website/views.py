from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)





