from flask import g, current_app
from datetime import datetime
import os

import click
import psycopg2.extras
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2

def get_db():
    """  Получить подключение к базе данных. """
    if 'db' not in g:
        g.db = psycopg2.connect(
            f"host={current_app.config['DATABASE_HOST']}\
                port={current_app.config['DATABASE_PORT']}\
                user={current_app.config['DATABASE_USER']}\
                password={current_app.config['DATABASE_PASSWORD']}\
                dbname={current_app.config['DATABASE_NAME']}\
            ",
            cursor_factory=psycopg2.extras.NamedTupleCursor
        )

    return g.db


def close_db(e=None):
    """ Закрыть подключение к базе данных. """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """ Инициализация базы данных. """
    db = get_db()

    try:
        with current_app.open_resource('schema.sql') as f:
            cur = db.cursor()
            cur.execute(f.read().decode('utf8'))
            db.commit()
    except Exception as e:
        print(f"{e}")
        raise e

def seed_db():
    db = get_db()

    try:
        with current_app.open_resource('seed.sql') as f:
            cur = db.cursor()
            cur.execute(f.read().decode('utf-8'))
            db.commit()
    except Exception as e:
        print(f"{e}")
        raise e


import shutil

def init_docs_folder():
    utd_document_folder = current_app.config['UTD_DOCS_UPLOAD_FOLDER']
    contract_document_folder = current_app.config['CONTRACT_DOCS_UPLOAD_FOLDER']
    
    # Remove existing folders if they exist
    if os.path.exists(utd_document_folder):
        shutil.rmtree(utd_document_folder)
    if os.path.exists(contract_document_folder):
        shutil.rmtree(contract_document_folder)
    
    # Create new folders
    os.makedirs(utd_document_folder, exist_ok=True)
    os.makedirs(contract_document_folder, exist_ok=True)


def current_user(user_id: int) -> tuple:
    """ Получение полной информации о пользователе """
    db = get_db()
    cur = db.cursor()
    error = None

    try:
        cur.execute("""
                SELECT 
                    users.id,
                    users.name,
                    users.second_name,
                    users.surname,
                    users.date_of_birth,
                    users.role,
                    user_roles.name AS role_name,
                    users.has_signature,
                    users.add_employee,
                    users.organization,
                    counterparties.name AS organization_name,
                    users.blocked,
                    users.login,
                    users.email,
                    users.send_tin,
                    users.created_at,
                    users.updated_at
                FROM 
                    users
                JOIN 
                    user_roles ON users.role = user_roles.id
                JOIN 
                    counterparties ON users.organization = counterparties.id
                WHERE 
                    users.id = %s""", (user_id,))
        current_user = cur.fetchone()
        if current_user is None:
            print(f"No user found with id: {user_id}")
            return None
    except Exception as e:
        print(f"Error fetching user with id {user_id}: {e}")
        return None

    return current_user

def get_counterparties() -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None

    try:
        cur.execute("""
                SELECT 
                    counterparties.id,
                    counterparties.name,
                    counterparties.tin,
                    counterparties.address,
                    counterparties.email,
                    counterparties.phone_number
                FROM 
                    counterparties""")
    except Exception as e:
        print(f"{e}")

    counterparties = cur.fetchall()

    return counterparties


def get_utd_document(document_id: int) -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None
    document = None
    try:
        cur.execute(
            """SELECT 
                    utd.id,
                    utd.number,
                    utd.counterparty,
                    cp1.name AS counterparty_name,
                    utd.creator,
                    u1.name AS creator_name,
                    u1.second_name AS creator_second_name,
                    u1.surname AS creator_surname,
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
                    u2.second_name AS sender_signature_second_name,
                    u2.surname AS sender_signature_surname,
                    utd.recipient_signature,
                    u3.name AS recipient_signature_name,
                    u3.second_name AS recipient_signature_second_name,
                    u3.surname AS recipient_signature_surname,
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
                    utd.id = %s ORDER BY utd.created_at DESC;""", (document_id,)
        )
        document = cur.fetchone()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)

    return document


def get_contract_document(document_id: int) -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None
    document = None
    try:
        cur.execute(
            """SELECT 
                    cd.id,
                    cd.number,
                    cd.counterparty,
                    cp1.name AS counterparty_name,
                    cd.creator,
                    u1.name AS creator_name,
                    u1.second_name AS creator_second_name,
                    u1.surname AS creator_surname,
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
                    u2.second_name AS provider_signature_second_name,
                    u2.surname AS provider_signature_surname,
                    cd.client_signature,
                    u3.name AS client_signature_name,
                    u3.second_name AS client_signature_second_name,
                    u3.surname AS client_signature_surname,
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
                    cd.id = %s ORDER BY cd.created_at DESC""", (document_id,)
        )
        document = cur.fetchone()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)

    return document


def get_utd_document_items(document_id: int) -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None
    items = None
    try:
        cur.execute("""SELECT * FROM utd_document_items WHERE utd_document_id = %s;""", (document_id,))
        items = cur.fetchall()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)

    return items


def get_user_roles() -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None
    user_roles = None
    try:
        cur.execute("""SELECT * FROM user_roles;""")
        user_roles = cur.fetchall()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)

    return user_roles


def get_register_requests() -> tuple:
    """  Получение заявок на регистрацию. """
    db = get_db()
    cur = db.cursor()
    error = None
    register_requests = None
    try:
        cur.execute(
            """SELECT
                    register_requests.id,
                    register_requests.user_id,
                    users.name AS user_name,
                    users.second_name AS user_second_name,
                    users.surname AS user_surname,
					counterparties.name as org_name,
                    register_requests.tin,
                    register_requests.completed,
                    register_requests.created_at,
                    register_requests.updated_at
                FROM register_requests
                JOIN users ON register_requests.user_id = users.id
				JOIN counterparties ON register_requests.tin = counterparties.tin
                ORDER BY register_requests.created_at DESC;""")
        register_requests = cur.fetchall()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)

    return register_requests


def get_register_request(req_id: int) -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None
    register_request = None
    try:
        cur.execute(
            """SELECT
                    register_requests.id,
                    register_requests.user_id,
                    users.name AS user_name,
                    users.second_name AS user_second_name,
                    users.surname AS user_surname,
                    counterparties.name as org_name,
                    register_requests.tin,
                    register_requests.completed,
                    register_requests.created_at,
                    register_requests.updated_at
                FROM register_requests
                JOIN users ON register_requests.user_id = users.id
                JOIN counterparties ON register_requests.tin = counterparties.tin
                WHERE register_requests.id = %s;""", (req_id,)
        )
        register_request = cur.fetchone()
    except Exception as e:
        error = f"DB: Произошла ошибка: {e}"
        print(error)

    return register_request 


@click.command('init-db')
def init_db_command():
    """ Команда для cli для инициализации базы данных. """
    init_db()
    click.echo("Successfully initialized the database.")

@click.command('seed-db')
def seed_db_command():
    """ Команда для cli для Заполнение базы данных """
    seed_db()
    click.echo("Successfully seeded the database.")

@click.command('init-docs-folder')
def init_docs_folder_command():
    """ Команда для cli для инициализации папок с документами. """
    init_docs_folder()
    click.echo("Successfully initialized the docs folder.")

# @click.command('create-super-user')
# @click.argument('login')
# @click.argument('password')
# def create_super_user(login: str, password: str):
#     """  Команда для cli для создания суперпользователя. """
#     db = get_db()

#     try:
#         cur = db.cursor()
#         cur.execute(
#             "INSERT INTO users (name, second_name, surname, date_of_born, role, organization, blocked, login, email, password_digest, created_at) VALUES \
#                 (%s, %s, %s, %s, %s, %s)",
#             ('admin', False, login, 'admin_email', generate_password_hash(password), datetime.now()))
#     except psycopg2.errors.UniqueViolation:
#         click.echo("User with this login already exists.")
#     except psycopg2.Error as e:
#         click.echo(f"Error: {e}")
#     else:
#         db.commit()
#         click.echo("Successfully created superuser.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(init_docs_folder_command)
    # app.cli.add_command(create_super_user)