from flask import Blueprint, render_template, abort, g, redirect, url_for
from jinja2 import TemplateNotFound

from EDM.auth import login_required
from EDM.databae import current_user

bp = Blueprint('dashboard', __name__, template_folder='templates')

@bp.route('/')
@login_required
def redirect_to_index():
    if current_user(g.user).role == 1:
        return redirect('/admin')
    return redirect('/dashboard')

@bp.route('/dashboard')
@login_required
def index():
    if current_user(g.user).role == 1:
        return redirect('/admin')
    return render_template('index.html.jinja', user=current_user(g.user))

