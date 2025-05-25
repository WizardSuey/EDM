import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from EDM.auth import login_required, requires_user_organization
from EDM.databae import get_db, current_user, get_counterparties

bp = Blueprint('counterparties', __name__, template_folder='templates/counterparties', url_prefix='/counterparties')


@bp.route('/counterparties')
@login_required
@requires_user_organization
def index():
    counterparties = get_counterparties()
    return render_template('counterparties/index.html.jinja', user=current_user(g.user), counterparties=counterparties)