import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from EDM.databae import get_db

bp = Blueprint('admin', __name__, template_folder='/admin', url_prefix='/admin')