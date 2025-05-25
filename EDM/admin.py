import functools
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from EDM.databae import get_db, current_user, get_register_requests, get_register_request
from EDM.auth import login_required
from EDM.add_user_form import AddUserForm
from EDM.add_counterparty_form import AddCounterpartyForm
from EDM.add_user_role_form import AddUserRoleForm
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('admin', __name__, template_folder='templates/admin', url_prefix='/admin')

def is_admin(view):
    @functools.wraps(view)
    def decorated_view(*args, **kwargs):
        if current_user(g.user) is None or current_user(g.user).role != 1:
            return redirect(url_for('dashboard.index'))
        return view(*args, **kwargs)
    return decorated_view

def is_user_can_add_employee(view):
    @functools.wraps(view)
    def decorated_view(*args, **kwargs):
        if current_user(g.user) is None or current_user(g.user).add_employee == False:
            return redirect('/dashboard')
        return view(*args, **kwargs)
    return decorated_view

@bp.route('/', methods=['GET', 'POST'])
@login_required
@is_admin
def redirect_to_index():
    return redirect(url_for('admin.index'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@is_admin
def index():
    return render_template('admin/index.html.jinja', user=current_user(g.user))


@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@is_user_can_add_employee
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        db = get_db()
        cur = db.cursor()
        password = generate_password_hash(form.password.data)
        try:
            cur.execute(
                """
                INSERT INTO users (name, second_name, surname, date_of_birth, role, has_signature, 
                                   add_employee, organization, blocked, login, email, send_tin, password_digest)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    form.name.data,
                    form.second_name.data,
                    form.surname.data,
                    form.date_of_birth.data,
                    form.role.data,
                    form.has_signature.data,
                    form.add_employee.data,
                    form.organization.data,
                    form.blocked.data,
                    form.login.data,
                    form.email.data,
                    form.send_tin.data,
                    password
                )
            )
            db.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.rollback()
            flash(f'Error adding user: {e}', 'danger')

    return render_template('add_user.html.jinja', form=form, user=current_user(g.user))


@bp.route('/add_counterparty', methods=['GET', 'POST'])
@login_required
@is_admin
def add_counterparty():
    form = AddCounterpartyForm()
    if form.validate_on_submit():
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                """
                INSERT INTO counterparties (name, tin, email, phone_number, address)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    form.name.data,
                    form.tin.data,
                    form.email.data,
                    form.phone_number.data,
                    form.address.data
                )
            )
            db.commit()
            flash('Counterparty added successfully!', 'success')
            print(f"Counterparty added successfully! {form.name.data}")
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.rollback()
            flash(f'Error adding counterparty: {e}', 'danger')

    return render_template('add_counterparty.html.jinja', form=form, user=current_user(g.user))


@bp.route('/submit_register_request/<int:req_id>', methods=['GET', 'POST'])
@login_required
@is_admin
def submit_register_request(req_id: int):
    """ Подтверждение заявки на регистрацию """
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT completed FROM register_requests WHERE id = %s", (req_id,))
        if cur.fetchone()[0]:
            print("Request already completed.", "info")
            return redirect(url_for('admin.register_requests'))
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)
        print(error, category="error")
        return redirect(url_for('admin.register_requests'))

    form = AddUserRoleForm(request.form)
    if request.method == "POST":
        if form.validate():
            role = form.role.data
            reg_request = get_register_request(req_id)
            try:
                cur.execute("UPDATE register_requests SET completed = %s WHERE id = %s", (True, req_id))
                db.commit()

                cur.execute("UPDATE register_requests SET updated_at = %s WHERE id = %s", (datetime.datetime.now(), req_id))
                db.commit()

                cur.execute("SELECT id FROM counterparties WHERE tin = %s", (reg_request.tin,))
                counterparty_id = cur.fetchone()

                cur.execute("UPDATE users SET role = %s, organization = %s WHERE id = %s", (role, counterparty_id, reg_request.user_id))
                db.commit()

                cur.execute("UPDATE users SET updated_at = %s WHERE id = %s", (datetime.datetime.now(), reg_request.user_id))
                db.commit()
                
                return redirect(url_for('admin.register_requests'))
            except Exception as e:
                error = f"DB: Произошла ошибка: {e}"
                print(error)
                flash(error, category="error")
        else:
            flash("Form validation failed.", "error")

    return render_template('complete_reg_req.html.jinja', form=form, user=current_user(g.user), req_id=req_id)


@bp.route('/register_requests', methods=['GET', 'POST'])
@login_required
@is_admin
def register_requests():
    """ Подтверждение заявок на регистрацию от пользователей """
    register_requests = get_register_requests()
    return render_template('register_requests.html.jinja', user=current_user(g.user), register_requests=register_requests)