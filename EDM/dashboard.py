from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from EDM.auth import login_required

bp = Blueprint('dashboard', __name__, template_folder='templates')

@bp.route('/dashboard')
@login_required
def index():
    return render_template('index.html.jinja')