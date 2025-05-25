import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from werkzeug.security import check_password_hash, generate_password_hash

from EDM.login_form import LoginForm
from EDM.register_form import RegisterForm
from EDM.tin_form import TinForm

from EDM.databae import get_db, current_user

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view


def requires_user_organization(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user = current_user(g.user)
        if user is None or user.organization == 99999:
            return redirect(url_for('auth.getting_start'))
        
        return view(**kwargs)
    
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_id
        print(f"Loaded user_id from session: {user_id}")

@bp.route("/login", methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('dashboard.index'))
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


@bp.route("/getting_start", methods=('GET', 'POST'))
@login_required
def getting_start():
    form = TinForm()
    if request.method == "POST":
        if form.validate():
            tin = form.tin.data
            user = current_user(g.user)
            if user.send_tin:
                return render_template("auth/getting_start.html.jinja", form=form, user=current_user(g.user))
            try:
                db = get_db()
                cur = db.cursor()
                cur.execute(
                    "SELECT * FROM counterparties WHERE tin = %s", (tin,)
                )

                counterparty = cur.fetchone()

                if counterparty is None:
                    error = "Неверный ИНН. Такой Организации не существует."
                    print(error)
                    flash(error, category="error")
                    return render_template("auth/getting_start.html.jinja", form=form, user=current_user(g.user))
                else:
                    cur.execute(
                        "INSERT INTO register_requests (user_id, tin) VALUES (%s, %s)", (user.id, tin)
                    )
                    cur.execute(
                        "UPDATE users SET send_tin = %s WHERE id = %s", (True, user.id)
                    )
                    db.commit()
            except Exception as e:
                error = f"DB: Произошла ошибка: {e}"
                print(error)
                flash(error, category="error")
                return render_template("auth/getting_start.html.jinja", form=form, user=current_user(g.user))
        else:
            error = "Форма не прошла валидацию"
            print(error)
            flash(error, category="error")
            return render_template("auth/getting_start.html.jinja", form=form, user=current_user(g.user))
        
    return render_template("auth/getting_start.html.jinja", form=form, user=current_user(g.user))


@bp.route("/register", methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate():
            error = None
            db = get_db()
            cur = db.cursor()
            try:
                cur.execute(
                    "INSERT INTO users (name, second_name, surname, date_of_birth, login, email, password_digest, organization, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (form.name.data, 
                     form.second_name.data, 
                     form.surname.data, 
                     form.date_of_birth.data, 
                     form.login.data, 
                     form.email.data, 
                     generate_password_hash(form.password.data),
                     99999,
                     99999)
                )
                db.commit()
                cur.execute(
                    "SELECT * FROM users WHERE login = %s", (form.login.data,)
                )
                user = cur.fetchone()
                session.clear()
                session['user_id'] = user.id
                return redirect(url_for("auth.getting_start"))
            except Exception as e:
                error = f"DB: Произошла ошибка: {e}"
                print(error)
                flash(error, category="error")
                return render_template("auth/register.html.jinja", form=form)

    return render_template("auth/register.html.jinja", form=form)


@bp.before_app_request
def has_user_organization():
    user = current_user(g.user)
    if user and user.organization is None:
        return redirect(url_for('auth.getting_start'))
    

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('dashboard.index'))