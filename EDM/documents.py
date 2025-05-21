import functools
import random
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)

from EDM.databae import get_db, current_user
from EDM.auth import login_required
from EDM.document_create_select_type_form import SelectCreateDocumentForm
from EDM.create_utd_form import UtdDocumentForm
from EDM.add_items_utd_form import UtdDocumentItemsForm
from EDM.create_contract_form import ContractDocumentForm

bp = Blueprint('documents', __name__, template_folder='templates/documents', url_prefix='/documents')


def organization_required(document_type):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(document_id, **kwargs):
            db = get_db()
            cur = db.cursor()
            if document_type == 'utd':
                cur.execute(
                    "SELECT creator_counterparty FROM utd_documents WHERE id = %s", (document_id,)
                )
            elif document_type == 'contract':
                cur.execute(
                    "SELECT creator_counterparty FROM contract_documents WHERE id = %s", (document_id,)
                )

            document = cur.fetchone()

            if document is None or document.creator_counterparty != current_user(g.user).organization:
                flash("У вас нет прав на редактирование этого докумета.", category="error")
                return redirect(url_for('dashboard.index'))

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


@bp.route('/outcoming', methods=['GET', 'POST'])
@login_required
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
                    creator_counterparty = %s;""", (current_user(g.user).organization,)
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
                    creator_counterparty = 1;""", (current_user(g.user).organization,)
            )
        con_documents = cur.fetchall()
    except Exception as e:
        print(f"{e}")
        error = f"DB: Произошла ошибка: {e}"
        flash(error, category="error")
    
    documents = []
    documents.extend(utd_documents)
    documents.extend(con_documents)
    print(documents)
    return render_template('outcoming.html.jinja', user=current_user(g.user), documents=documents)

@bp.route('/create/upd/create/<int:document_id>/add_items', methods=['GET', 'POST'])
@login_required
@organization_required(document_type='utd')
def utd_add_items(document_id):
    """ Страница добавления товаров в УПД """
    if check_document_status(document_id, 'utd')[0] != 1:
        return redirect(url_for('dashboard.index'))
    form = UtdDocumentItemsForm(request.form, data={
        'utd_document_id': document_id
    })

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

            return redirect(url_for('documents.utd_add_items', document_id=document_id))
        except Exception as e:
            print(f"{e}")
            error = f"DB: Произошла ошибка: {e}"
            flash(error, category="error")

    elif request.method == "POST":
        error = f"Произошла ошибка: {form.errors}"
        print(form.errors)
        flash(error, category="error")

    return render_template('documents/add_items_utd.html.jinja', user=current_user(g.user), document_id=document_id, form=form)

@bp.route('/create/utd/create', methods=['GET', 'POST'])
@login_required
def create_upd():
    """ Страница создания УПД """
    form = UtdDocumentForm(request.form, data={
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
    if request.method == "POST" and form.validate():
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
            return redirect(url_for('documents.utd_add_items', document_id=document.id))
        except Exception as e:
            print(f"{e}")
            error = f"Произошла ошибка: {e}"
            flash(error, category="error")

    elif request.method == "POST":
        error = f"Произошла ошибка: {form.errors}"
        print(form.errors)
        flash(error, category="error")

    return render_template('documents/create_utd.html.jinja', user=current_user(g.user), current_date=current_date, form=form)


@bp.route('/create/contract/create/<int:document_id>/add_text', methods=['GET', 'POST'])
@login_required
@organization_required(document_type='contract')
def contract_add_text(document_id):
    """ Страница добавления текста в Договор """
    if check_document_status(document_id, 'contract')[0] != 1:
        return redirect(url_for('dashboard.index'))
    return render_template('documents/add_text_contract.html.jinja', user=current_user(g.user), document_id=document_id)

@bp.route('/create/contract/create', methods=['GET', 'POST'])
@login_required
def create_contract():
    """ Страница создания Договора """
    form = ContractDocumentForm(request.form, data={
        'number': generate_document_number('contract'),
        'creator': current_user(g.user).id,
        'creator_counterparty': current_user(g.user).organization,
        'document_type': 2,
        'document_status': 1,
        'provider_signature': None,
        'client_signature': None,
        'date_of_receipt': None,
        'file_path': None,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    })
    current_date = datetime.datetime.now().strftime('%Y.%m.%d')
    if request.method == "POST" and form.validate():
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
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO contract_documents (number, counterparty, creator, creator_counterparty, document_type, document_status, provider, provider_base, client, client_base, address) VALUES \
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (number, counterparty, creator, creator_counterparty, document_type, document_status, provider, provider_base, client, client_base, address)
            )
            db.commit()
            cur.execute(
                "SELECT * FROM contract_documents WHERE number = %s", (number,)
            )
            document = cur.fetchone()
            print(document)
            print(f"Документ {number} создан\nDataBase ID: {document.id}")
            return redirect(url_for('documents.contract_add_text', user=current_user(g.user), document_id=document.id))
        except Exception as e:
            print(f"{e}")
            error = f"Произошла ошибка: {e}"
            flash(error, category="error")

    elif request.method == "POST":
        error = f"Произошла ошибка: {form.errors}"
        print(form.errors)
        flash(error, category="error")

    return render_template('documents/create_contract.html.jinja', user=current_user(g.user), form=form, current_date=current_date)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
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

@bp.route('/incoming')
@login_required
def incoming():
    """ Страница с входящими документами """

@bp.route('/outgoing')
@login_required
def outgoing():
    """ Страница с исходящими документами """