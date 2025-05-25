import functools
import random
import datetime
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.utils import secure_filename

from EDM.databae import get_db, current_user, get_contract_document, get_utd_document, get_utd_document_items
from EDM.auth import login_required, requires_user_organization
from EDM.document_create_select_type_form import SelectCreateDocumentForm
from EDM.create_utd_form import UtdDocumentForm
from EDM.add_items_utd_form import UtdDocumentItemsForm
from EDM.create_contract_form import ContractDocumentForm
from EDM.add_text_contract_form import ContractDocumentAddTextForm

bp = Blueprint('documents', __name__, template_folder='templates/documents', url_prefix='/documents')


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def organization_required(document_type):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(document_id, **kwargs):
            db = get_db()
            cur = db.cursor()
            if document_type == 'utd':
                cur.execute(
                    "SELECT creator_counterparty, counterparty FROM utd_documents WHERE id = %s", (document_id,)
                )
            elif document_type == 'contract':
                cur.execute(
                    "SELECT creator_counterparty, counterparty FROM contract_documents WHERE id = %s", (document_id,)
                )

            document = cur.fetchone()

            if document is None or (document.creator_counterparty != current_user(g.user).organization and document.counterparty != current_user(g.user).organization):
                flash("У вас нет прав на Просмотр или Редактирование этого документа.", category="error")
                return redirect(url_for('documents.incoming')) 

            return view(document_id, **kwargs)

        return wrapped_view
    return decorator


def check_document_status(document_id, document_type):
    db = get_db()
    cur = db.cursor()
    try:
        if document_type == 'utd':
            cur.execute("SELECT document_status FROM utd_documents WHERE id = %s", (document_id,))
        elif document_type == 'contract':
            cur.execute("SELECT document_status FROM contract_documents WHERE id = %s", (document_id,))
    except Exception as e:
        print(f"{e}")
        flash(f"DB: Произошла ошибка: {e}", category="error")
    status = cur.fetchone()
    return status


def generate_document_number(document_type) -> str:
    prefix = ""
    if document_type == 'utd':
        prefix = "utd2"
    elif document_type == 'contract':
        prefix = "con5"
    
    random_number = random.randint(100000, 999999)
    date_str = datetime.datetime.now().strftime('%Y%m%d')

    return f"{prefix}{random_number}{date_str}"

@bp.route('/view/utd/<int:document_id>', methods=['GET', 'POST'])
@login_required
@organization_required('utd')
def view_utd(document_id):
    """ просмотр УПД """
    error = None
    
    document = get_utd_document(document_id)
    document_items = get_utd_document_items(document_id)
    document_files = None
    document_folder = os.path.join(current_app.config['UTD_DOCS_UPLOAD_FOLDER'], str(document_id))
    creator: tuple = None
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (document.creator,))
        creator = cur.fetchone()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(f"{error}")
        flash(f"{error}", category="error")

    if document is None:
        flash("Документ не найден.", category="error")
        return redirect(request.referrer)
    
    if os.path.exists(document_folder):
        document_files = [f for f in os.listdir(document_folder)]

    return render_template('utd_view.html.jinja', user=current_user(g.user), 
                           document = document, creator=creator, document_items=document_items, document_files=document_files)


@bp.route('/view/contract/<int:document_id>', methods=['GET', 'POST'])
@login_required
@organization_required('contract')
def view_contract(document_id):
    """ просмотр Контракта """
    error = None
    
    document = get_contract_document(document_id)
    document_files = None
    document_folder = os.path.join(current_app.config['CONTRACT_DOCS_UPLOAD_FOLDER'], str(document_id))
    creator: tuple = None
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (document.creator,))
        creator = cur.fetchone()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(f"{error}")
        flash(f"{error}", category="error")

    if document is None:
        flash("Документ не найден.", category="error")
        return redirect(request.referrer)
    
    if os.path.exists(document_folder):
        document_files = [f for f in os.listdir(document_folder)]

    return render_template('contract_view.html.jinja', user=current_user(g.user), 
                           document = document, creator=creator, document_files=document_files)


@bp.route('/incoming', methods=['GET', 'POST'])
@login_required
@requires_user_organization
def incoming():
    """" Страница входящих документов """
    db = get_db()
    cur = db.cursor()
    error = None
    utd_documents = None
    con_documents = None
    try:
        cur.execute(
            """SELECT 
                    utd.id,
                    utd.number,
                    utd.counterparty,
                    cp1.name AS counterparty_name,
                    utd.creator,
                    u1.name AS creator_name,
                    utd.creator_counterparty,
                    cp2.name AS creator_counterparty_name,
                    utd.consignee,
                    cp3.name AS consignee_name,
                    utd.provider,
                    cp4.name AS provider_name,
                    utd.payer,
                    cp5.name AS payer_name,
                    utd.amount,
                    utd.document_type,
                    dt.name AS document_type_name,
                    utd.document_status,
                    ds.name AS document_status_name,
                    utd.sender_signature,
                    u2.name AS sender_signature_name,
                    utd.recipient_signature,
                    u3.name AS recipient_signature_name,
                    utd.date_of_receipt,
                    utd.file_path,
                    utd.created_at,
                    utd.updated_at
                FROM 
                    utd_documents utd
                JOIN 
                    counterparties cp1 ON utd.counterparty = cp1.id
                JOIN 
                    users u1 ON utd.creator = u1.id
                JOIN 
                    counterparties cp2 ON utd.creator_counterparty = cp2.id
                JOIN 
                    counterparties cp3 ON utd.consignee = cp3.id
                JOIN 
                    counterparties cp4 ON utd.provider = cp4.id
                JOIN 
                    counterparties cp5 ON utd.payer = cp5.id
                JOIN 
                    document_types dt ON utd.document_type = dt.id
                JOIN 
                    document_statuses ds ON utd.document_status = ds.id
                LEFT JOIN 
                    users u2 ON utd.sender_signature = u2.id
                LEFT JOIN 
                    users u3 ON utd.recipient_signature = u3.id
                WHERE 
                    counterparty = %s ORDER BY created_at DESC;""", (current_user(g.user).organization,)
            )
        utd_documents = cur.fetchall()
        cur.execute(
            """SELECT 
                    cd.id,
                    cd.number,
                    cd.counterparty,
                    cp1.name AS counterparty_name,
                    cd.creator,
                    u1.name AS creator_name,
                    cd.creator_counterparty,
                    cp2.name AS creator_counterparty_name,
                    cd.document_type,
                    dt.name AS document_type_name,
                    cd.document_status,
                    ds.name AS document_status_name,
                    cd.provider,
                    cp3.name AS provider_name,
                    cd.provider_base,
                    cd.client,
                    cp4.name AS client_name,
                    cd.client_base,
                    cd.address,
                    cd.provider_signature,
                    u2.name AS provider_signature_name,
                    cd.client_signature,
                    u3.name AS client_signature_name,
                    cd.date_of_receipt,
                    cd.file_path,
                    cd.created_at,
                    cd.updated_at
                FROM 
                    contract_documents cd
                JOIN 
                    counterparties cp1 ON cd.counterparty = cp1.id
                JOIN 
                    users u1 ON cd.creator = u1.id
                JOIN 
                    counterparties cp2 ON cd.creator_counterparty = cp2.id
                JOIN 
                    document_types dt ON cd.document_type = dt.id
                JOIN 
                    document_statuses ds ON cd.document_status = ds.id
                JOIN 
                    counterparties cp3 ON cd.provider = cp3.id
                JOIN 
                    counterparties cp4 ON cd.client = cp4.id
                LEFT JOIN 
                    users u2 ON cd.provider_signature = u2.id
                LEFT JOIN 
                    users u3 ON cd.client_signature = u3.id
                WHERE
                    counterparty = %s ORDER BY created_at DESC;""", (current_user(g.user).organization,)
            )
        con_documents = cur.fetchall()
    except Exception as e:
        print(f"{e}")
        error = f"DB: Произошла ошибка: {e}"
        flash(error, category="error")
    
    documents = []
    if utd_documents:
        documents.extend(utd_documents)
    if con_documents:
        documents.extend(con_documents)
    print(documents)
    return render_template('incoming.html.jinja', user=current_user(g.user), documents=documents)

@bp.route('/outcoming', methods=['GET', 'POST'])
@login_required
@requires_user_organization
def outcoming():
    """" Страница исходящих документов """
    db = get_db()
    cur = db.cursor()
    error = None
    utd_documents = None
    con_documents = None
    try:
        cur.execute(
            """SELECT 
                    utd.id,
                    utd.number,
                    utd.counterparty,
                    cp1.name AS counterparty_name,
                    utd.creator,
                    u1.name AS creator_name,
                    utd.creator_counterparty,
                    cp2.name AS creator_counterparty_name,
                    utd.consignee,
                    cp3.name AS consignee_name,
                    utd.provider,
                    cp4.name AS provider_name,
                    utd.payer,
                    cp5.name AS payer_name,
                    utd.amount,
                    utd.document_type,
                    dt.name AS document_type_name,
                    utd.document_status,
                    ds.name AS document_status_name,
                    utd.sender_signature,
                    u2.name AS sender_signature_name,
                    utd.recipient_signature,
                    u3.name AS recipient_signature_name,
                    utd.date_of_receipt,
                    utd.file_path,
                    utd.created_at,
                    utd.updated_at
                FROM 
                    utd_documents utd
                JOIN 
                    counterparties cp1 ON utd.counterparty = cp1.id
                JOIN 
                    users u1 ON utd.creator = u1.id
                JOIN 
                    counterparties cp2 ON utd.creator_counterparty = cp2.id
                JOIN 
                    counterparties cp3 ON utd.consignee = cp3.id
                JOIN 
                    counterparties cp4 ON utd.provider = cp4.id
                JOIN 
                    counterparties cp5 ON utd.payer = cp5.id
                JOIN 
                    document_types dt ON utd.document_type = dt.id
                JOIN 
                    document_statuses ds ON utd.document_status = ds.id
                LEFT JOIN 
                    users u2 ON utd.sender_signature = u2.id
                LEFT JOIN 
                    users u3 ON utd.recipient_signature = u3.id
                WHERE 
                    creator_counterparty = %s ORDER BY created_at DESC;""", (current_user(g.user).organization,)
            )
        utd_documents = cur.fetchall()
        cur.execute(
            """SELECT 
                    cd.id,
                    cd.number,
                    cd.counterparty,
                    cp1.name AS counterparty_name,
                    cd.creator,
                    u1.name AS creator_name,
                    cd.creator_counterparty,
                    cp2.name AS creator_counterparty_name,
                    cd.document_type,
                    dt.name AS document_type_name,
                    cd.document_status,
                    ds.name AS document_status_name,
                    cd.provider,
                    cp3.name AS provider_name,
                    cd.provider_base,
                    cd.client,
                    cp4.name AS client_name,
                    cd.client_base,
                    cd.address,
                    cd.provider_signature,
                    u2.name AS provider_signature_name,
                    cd.client_signature,
                    u3.name AS client_signature_name,
                    cd.date_of_receipt,
                    cd.file_path,
                    cd.created_at,
                    cd.updated_at
                FROM 
                    contract_documents cd
                JOIN 
                    counterparties cp1 ON cd.counterparty = cp1.id
                JOIN 
                    users u1 ON cd.creator = u1.id
                JOIN 
                    counterparties cp2 ON cd.creator_counterparty = cp2.id
                JOIN 
                    document_types dt ON cd.document_type = dt.id
                JOIN 
                    document_statuses ds ON cd.document_status = ds.id
                JOIN 
                    counterparties cp3 ON cd.provider = cp3.id
                JOIN 
                    counterparties cp4 ON cd.client = cp4.id
                LEFT JOIN 
                    users u2 ON cd.provider_signature = u2.id
                LEFT JOIN 
                    users u3 ON cd.client_signature = u3.id
                WHERE
                    creator_counterparty = %s ORDER BY created_at DESC;""", (current_user(g.user).organization,)
            )
        con_documents = cur.fetchall()
    except Exception as e:
        print(f"{e}")
        error = f"DB: Произошла ошибка: {e}"
        flash(error, category="error")
    
    documents = []
    if utd_documents:
        documents.extend(utd_documents)
    if con_documents:
        documents.extend(con_documents)
    print(documents)
    return render_template('outcoming.html.jinja', user=current_user(g.user), documents=documents)

@bp.route('/create/upd/create/<int:document_id>/add_items', methods=['GET', 'POST'])
@login_required
@organization_required(document_type='utd')
def utd_add_items(document_id):
    """ Страница добавления товаров в УПД """
    if check_document_status(document_id, 'utd')[0] != 1 and check_document_status(document_id, 'utd')[0] != 2:
        return redirect(url_for('documents.outcoming'))
    if current_user(g.user).organization != get_utd_document(document_id).creator_counterparty:
        return redirect(url_for('documents.outcoming'))
    form = UtdDocumentItemsForm(request.form, data={
        'utd_document_id': document_id
    })

    document_number = get_utd_document(document_id).number
    document_items = get_utd_document_items(document_id)
    if document_items is None:
        document_items = None

    if request.method == 'POST' and form.validate():
        error = None
        db = get_db()
        cur = db.cursor()
        try:
            amount = 0
            product_names = request.form.getlist('product_name')
            product_quantities = request.form.getlist('product_quantity')
            product_prices = request.form.getlist('product_price')
            product_sums = request.form.getlist('product_sum')

            for i in range(len(product_names)):
                product_name = product_names[i]
                product_quantity = product_quantities[i]
                product_price = product_prices[i]
                product_sum = product_sums[i]
                amount += float(product_sum)
                cur.execute(
                    "INSERT INTO utd_document_items (utd_document_id, product_name, product_quantity, product_price, product_sum) VALUES \
                        (%s, %s, %s, %s, %s)",
                    (document_id, product_name, product_quantity, product_price, product_sum)
                )
            print(f"Total amount: {amount}")
            cur.execute(
                "UPDATE utd_documents SET amount = amount + %s, document_status = 2 WHERE id = %s",
                (amount, document_id)
            )
            cur.execute(
                "UPDATE utd_documents SET sender_signature = %s WHERE id = %s",
                (current_user(g.user).id, document_id)
            )
            cur.execute(
                "UPDATE utd_documents SET updated_at = %s WHERE id = %s",
                (datetime.datetime.now(), document_id)
            )
            db.commit()

            return redirect(url_for('documents.outcoming'))
        except Exception as e:
            print(f"{e}")
            error = f"DB: Произошла ошибка: {e}"
            flash(error, category="error")

    elif request.method == "POST":
        error = f"Произошла ошибка: {form.errors}"
        print(form.errors)
        flash(error, category="error")

    return render_template('documents/add_items_utd.html.jinja', user=current_user(g.user), document_id=document_id, 
                           document_number=document_number, form=form, document_items=document_items)

@bp.route('/create/utd/create', methods=['GET', 'POST'])
@login_required
@requires_user_organization
def create_upd():
    """ Страница создания УПД """
    form = UtdDocumentForm(data={
        'number': generate_document_number('utd'),
        'creator': current_user(g.user).id,
        'creator_counterparty': current_user(g.user).organization,
        'amount': 0,
        'document_type': 1,
        'document_status': 1,
        'sender_signature': None,
        'recipient_signature': None,
        'date_of_receipt': None,
        'file_path': None,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    })
    current_date = datetime.datetime.now().strftime('%Y.%m.%d')
    if request.method == "POST":
        if form.validate_on_submit():
            error = None
            number = form.number.data
            counterparty = form.counterparty.data
            creator = form.creator.data
            creator_counterparty = form.creator_counterparty.data
            consignee = form.consignee.data
            provider = form.provider.data
            payer = form.payer.data
            amount = form.amount.data
            document_type = form.document_type.data
            document_status = form.document_status.data
            files = form.files.data

            db = get_db()
            cur = db.cursor()
            try:
                cur.execute(
                    "INSERT INTO utd_documents (number, counterparty, creator, creator_counterparty, consignee, provider, payer, amount, document_type, document_status) VALUES \
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (number, counterparty, creator, creator_counterparty, consignee, provider, payer, amount, document_type, document_status)
                )
                db.commit()
                cur.execute(
                    "SELECT * FROM utd_documents WHERE number = %s", (number,)
                )
                document = cur.fetchone()
                print(document)
                print(f"Документ {number} создан\nDataBase ID: {document.id}")

                document_folder = os.path.join(current_app.config['UTD_DOCS_UPLOAD_FOLDER'], str(document.id))
                os.makedirs(document_folder, exist_ok=True)

                for index, file in enumerate(files, start=1):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(document_folder, f"{index}.{filename.split('.')[-1]}")
                    file.save(file_path)

                cur.execute(
                    "UPDATE utd_documents SET file_path = %s WHERE id = %s",
                    (document_folder, document.id)
                )
                cur.execute(
                    "UPDATE utd_documents SET updated_at = %s WHERE id = %s",
                    (datetime.datetime.now(), document.id)
                )
                db.commit()

                return redirect(url_for('documents.utd_add_items', document_id=document.id))
            except Exception as e:
                print(f"{e}")
                error = f"Произошла ошибка: {e}"
                flash(error, category="error")

        else:
            error = f"Произошла ошибка: {form.errors}"
            print(form.errors)
            flash(error, category="error")

    return render_template('documents/create_utd.html.jinja', user=current_user(g.user), current_date=current_date, form=form)


@bp.route('/create/contract/create', methods=['GET', 'POST'])
@login_required
@requires_user_organization
def create_contract():
    """ Страница создания Договора """
    form = ContractDocumentForm(data={
        'number': generate_document_number('contract'),
        'creator': current_user(g.user).id,
        'creator_counterparty': current_user(g.user).organization,
        'document_type': 2,
        'document_status': 1,
        'provider_signature': None,
        'sender_signature': current_user(g.user).id,
        'date_of_receipt': None,
        'file_path': None,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    })
    current_date = datetime.datetime.now().strftime('%Y.%m.%d')
    
    if request.method == "POST":
        if form.validate_on_submit():
            error = None
            number = form.number.data
            counterparty = form.counterparty.data
            creator = form.creator.data
            creator_counterparty = form.creator_counterparty.data
            document_type = form.document_type.data
            document_status = form.document_status.data
            provider = form.provider.data
            provider_base = form.provider_base.data
            client = form.client.data
            client_base = form.client_base.data
            address = form.address.data
            client_signature = form.sender_signature.data
            files = form.files.data

            db = get_db()
            cur = db.cursor()
            try:
                cur.execute(
                    "INSERT INTO contract_documents (number, counterparty, creator, creator_counterparty, document_type, document_status, provider, provider_base, client, client_base, address, client_signature) VALUES \
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (number, counterparty, creator, creator_counterparty, document_type, document_status, provider, provider_base, client, client_base, address, client_signature)
                )
                db.commit()
                cur.execute(
                    "SELECT * FROM contract_documents WHERE number = %s", (number,)
                )
                document = cur.fetchone()
                print(document)
                print(f"Документ {number} создан\nDataBase ID: {document.id}")

                # Handle file uploads
                if files:
                    document_folder = os.path.join(current_app.config['CONTRACT_DOCS_UPLOAD_FOLDER'], str(document.id))
                    os.makedirs(document_folder, exist_ok=True)

                    for index, file in enumerate(files, start=1):
                        if file:
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(document_folder, f"{index}.{filename.split('.')[-1]}")
                            file.save(file_path)

                    cur.execute(
                        "UPDATE contract_documents SET file_path = %s WHERE id = %s",
                        (document_folder, document.id)
                    )
                    cur.execute(
                        "UPDATE contract_documents SET document_status = 2 WHERE id = %s",
                        (document.id,)
                    )
                    cur.execute(
                        "UPDATE contract_documents SET updated_at = %s WHERE id = %s",
                        (datetime.datetime.now(), document.id)
                    )
                    db.commit()

                    return redirect(url_for('documents.outcoming'))
                else:
                    print("No files uploaded.")

            except Exception as e:
                print(f"{e}")
                error = f"Произошла ошибка: {e}"
                flash(error, category="error")

        else:
            error = f"Произошла ошибка: {form.errors}"
            print(form.errors)
            flash(error, category="error")

    return render_template('documents/create_contract.html.jinja', user=current_user(g.user), form=form, current_date=current_date)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@requires_user_organization
def create():    
    """ Страница создания документа """
    form = SelectCreateDocumentForm(request.form)
    if request.method == "POST" and form.validate():
        document_type = form.document_type.data
        error = None
        if document_type == 'УПД':
            return redirect(url_for('documents.create_upd'))
        elif document_type == 'Договор':
            return redirect(url_for('documents.create_contract'))

    return render_template('documents/create.html.jinja', user=current_user(g.user), form=form)


@bp.route('/receive/<int:document_type>/<int:document_id>', methods=['GET', 'POST'])
@login_required
def receive_document(document_type, document_id):
    """ Метод принятия документа """
    db = get_db()
    cur = db.cursor()
    error = None
    if document_type == 1:
        cur.execute(
            "SELECT creator_counterparty, counterparty FROM utd_documents WHERE id = %s", (document_id,)
        )
    elif document_type == 2:
        cur.execute(
            "SELECT creator_counterparty, counterparty FROM contract_documents WHERE id = %s", (document_id,)
        )

    document = cur.fetchone()

    if document is None or (document.creator_counterparty != current_user(g.user).organization and document.counterparty != current_user(g.user).organization):
        flash("У вас нет прав на Просмотр или Редактирование этого документа.", category="error")
        return redirect(url_for('documents.incoming'))

    if document_type == 1:
        cur.execute("UPDATE utd_documents SET document_status = 3 WHERE id = %s", (document_id,))
        cur.execute("UPDATE utd_documents SET date_of_receipt = %s WHERE id = %s", (datetime.datetime.now(), document_id))
    elif document_type == 2:
        cur.execute("UPDATE contract_documents SET document_status = 3 WHERE id = %s", (document_id,))
        cur.execute("UPDATE contract_documents SET date_of_receipt = %s WHERE id = %s", (datetime.datetime.now(), document_id))

    db.commit()
    return redirect(url_for('documents.incoming'))


@bp.route('/sign/<int:document_type>/<int:document_id>', methods=['GET', 'POST'])
@login_required
@requires_user_organization
def sign_document(document_type, document_id):
    """ Метод подписания документа """
    db = get_db()
    cur = db.cursor()
    error = None
    if document_type == 1:
        cur.execute(
            "SELECT creator_counterparty, counterparty FROM utd_documents WHERE id = %s", (document_id,)
        )
    elif document_type == 2:
        cur.execute(
            "SELECT creator_counterparty, counterparty FROM contract_documents WHERE id = %s", (document_id,)
        )

    document = cur.fetchone()

    if document is None or (document.creator_counterparty != current_user(g.user).organization and document.counterparty != current_user(g.user).organization):
        flash("У вас нет прав на Просмотр или Редактирование этого документа.", category="error")
        return redirect(url_for('documents.incoming'))

    if document_type == 1:
        cur.execute("UPDATE utd_documents SET recipient_signature = %s WHERE id = %s", (current_user(g.user).id, document_id,))
        cur.execute("UPDATE utd_documents SET document_status = 5 WHERE id = %s", (document_id,))
    elif document_type == 2:
        cur.execute("UPDATE contract_documents SET provider_signature = %s WHERE id = %s", (current_user(g.user).id, document_id,))
        cur.execute("UPDATE contract_documents SET document_status = 5 WHERE id = %s", (document_id,))

    db.commit()
    return redirect(url_for('documents.incoming'))


@bp.route('/edit/utd/<int:document_id>', methods=['GET', 'POST'])
@login_required
@organization_required(document_type='utd')
def edit_utd(document_id):
    """ Страница редактирования документа """
    db = get_db()
    cur = db.cursor()

    # Retrieve the existing document and items
    document = get_utd_document(document_id)
    document_folder = os.path.join(current_app.config['UTD_DOCS_UPLOAD_FOLDER'], str(document_id))
    document_files = None
    if os.path.exists(document_folder):
        document_files = [f for f in os.listdir(document_folder)]

    # Initialize forms with existing data
    main_form = UtdDocumentForm(data={
        'number': document.number,
        'counterparty': document.counterparty,
        'creator': document.creator,
        'creator_counterparty': document.creator_counterparty,
        'consignee': document.consignee,
        'provider': document.provider,
        'payer': document.payer,
        'amount': document.amount,
        'document_type': document.document_type,
        'document_status': document.document_status,
        'sender_signature': document.sender_signature,
        'recipient_signature': document.recipient_signature,
        'date_of_receipt': document.date_of_receipt,
        'files': document_files,
        'file_path': document.file_path
    })

    # Process form submission
    if request.method == "POST":
        if main_form.validate_on_submit():
            error = None
            number = main_form.number.data
            counterparty = main_form.counterparty.data
            creator = main_form.creator.data
            creator_counterparty = main_form.creator_counterparty.data
            consignee = main_form.consignee.data
            provider = main_form.provider.data
            payer = main_form.payer.data
            amount = main_form.amount.data
            document_type = main_form.document_type.data
            document_status = main_form.document_status.data
            sender_signature = main_form.sender_signature.data
            recipient_signature = main_form.recipient_signature.data
            date_of_receipt = main_form.date_of_receipt.data
            file_path = main_form.file_path.data

            # Handle file uploads
            files = request.files.getlist('files')
            os.makedirs(document_folder, exist_ok=True)

            # Get the current number of files in the folder to continue numbering
            existing_files = os.listdir(document_folder)
            start_index = len(existing_files) + 1

            for index, file in enumerate(files, start=start_index):
                if file:
                    filename = secure_filename(file.filename)
                    file_extension = filename.split('.')[-1]
                    file_path = os.path.join(document_folder, f"{index}.{file_extension}")
                    file.save(file_path)

            try:
                cur.execute(
                    """
                    UPDATE utd_documents
                    SET number = %s, counterparty = %s, creator = %s, creator_counterparty = %s,
                        consignee = %s, provider = %s, payer = %s, amount = %s, document_type = %s,
                        document_status = %s, sender_signature = %s, recipient_signature = %s,
                        date_of_receipt = %s, file_path = %s, updated_at = %s
                    WHERE id = %s
                    """,
                    (number, counterparty, creator, creator_counterparty, consignee, provider, payer,
                    amount, document_type, document_status, sender_signature, recipient_signature,
                    date_of_receipt, document_folder, datetime.datetime.now(), document_id)
                )
                db.commit()
                flash("Документ успешно обновлен.", category="success")
                return redirect(url_for('documents.view_utd', document_id=document_id))
            except Exception as e:
                error = f"DB: Произошла ошибка: {e}"
                flash(f"{error}", category="error")
                print(error)
        else:
            error = f"Произошла ошибка: {main_form.errors}"
            print(main_form.errors)
            flash(error, category="error")

    return render_template('documents/edit_utd.html.jinja', user=current_user(g.user), document=document, main_form=main_form,
                           document_files=document_files)


@bp.route('/edit/contract/<int:document_id>', methods=['GET', 'POST'])  
@login_required
@organization_required(document_type='contract')
def edit_contract(document_id):
    """ Страница редактирования документа """
    db = get_db()
    cur = db.cursor()

    # Retrieve the existing document
    document = get_contract_document(document_id)
    document_folder = os.path.join(current_app.config['CONTRACT_DOCS_UPLOAD_FOLDER'], str(document_id))
    document_files = None
    if os.path.exists(document_folder):
        document_files = [f for f in os.listdir(document_folder)]

    # Initialize form with existing data
    main_form = ContractDocumentForm(data={
        'number': document.number,
        'counterparty': document.counterparty,
        'creator': document.creator,
        'creator_counterparty': document.creator_counterparty,
        'provider': document.provider,
        'provider_base': document.provider_base,
        'client': document.client,
        'client_base': document.client_base,
        'address': document.address,
        'document_type': document.document_type,
        'document_status': document.document_status,
        'sender_signature': document.provider_signature,  # Adjusted to match form field
        'recipient_signature': document.client_signature,  # Adjusted to match form field
        'date_of_receipt': document.date_of_receipt,
        'file_path': document.file_path
    })

    # Process form submission
    if request.method == "POST":
        if main_form.validate_on_submit():
            error = None
            number = main_form.number.data
            counterparty = main_form.counterparty.data
            creator = main_form.creator.data
            creator_counterparty = main_form.creator_counterparty.data
            provider = main_form.provider.data
            provider_base = main_form.provider_base.data
            client = main_form.client.data
            client_base = main_form.client_base.data
            address = main_form.address.data
            document_type = main_form.document_type.data
            document_status = main_form.document_status.data
            provider_signature = main_form.sender_signature.data  # Adjusted to match form field
            client_signature = main_form.recipient_signature.data  # Adjusted to match form field
            date_of_receipt = main_form.date_of_receipt.data
            file_path = main_form.file_path.data

            # Handle file uploads
            files = request.files.getlist('files')
            os.makedirs(document_folder, exist_ok=True)

            # Get the current number of files in the folder to continue numbering
            existing_files = os.listdir(document_folder)
            start_index = len(existing_files) + 1

            for index, file in enumerate(files, start=start_index):
                if file:
                    filename = secure_filename(file.filename)
                    file_extension = filename.split('.')[-1]
                    file_path = os.path.join(document_folder, f"{index}.{file_extension}")
                    file.save(file_path)

            try:
                cur.execute(
                    """
                    UPDATE contract_documents
                    SET number = %s, counterparty = %s, creator = %s, creator_counterparty = %s,
                        provider = %s, provider_base = %s, client = %s, client_base = %s, address = %s,
                        document_type = %s, document_status = %s, provider_signature = %s, client_signature = %s,
                        date_of_receipt = %s, file_path = %s, updated_at = %s
                    WHERE id = %s
                    """,
                    (number, counterparty, creator, creator_counterparty, provider, provider_base, client,
                    client_base, address, document_type, document_status, provider_signature, client_signature,
                    date_of_receipt, document_folder, datetime.datetime.now(), document_id)
                )
                db.commit()
                flash("Документ успешно обновлен.", category="success")
                return redirect(url_for('documents.view_contract', document_id=document_id))
            except Exception as e:
                error = f"DB: Произошла ошибка: {e}"
                flash(f"{error}", category="error")
                print(error)
        else:
            error = f"Произошла ошибка: {main_form.errors}"
            print(main_form.errors)
            flash(error, category="error")

    return render_template('documents/edit_contract.html.jinja', user=current_user(g.user), document=document, main_form=main_form,
                           document_files=document_files)