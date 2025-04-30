import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from EDM.databae import get_db
from EDM.auth import login_required

bp = Blueprint('documents', __name__, template_folder='/documents', url_prefix='/documents')

@bp.route('/incoming')
@login_required
def incoming():
    """ Страница с входящими документами """

@bp.route('/outgoing')
@login_required
def outgoing():
    """ Страница с исходящими документами """
