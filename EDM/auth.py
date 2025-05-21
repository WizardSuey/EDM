import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from werkzeug.security import check_password_hash, generate_password_hash

from EDM.login_form import LoginForm

from EDM.databae import get_db, current_user

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_id

@bp.route("/login", methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        login = form.login.data
        password = form.password.data
        db = get_db()
        cur = db.cursor()
        error = None
        cur.execute(
            "SELECT * FROM users WHERE login = %s", (login,)
        )

        user = cur.fetchone()

        if user is None:
            error = "Неверный логин"
        elif not check_password_hash(user.password_digest, password):
            error = "Неверный пароль"

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for("dashboard.index"))

        flash(error, category="error")

    return render_template("auth/login.html.jinja", form=form)

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('dashboard.index'))