from flask import g, current_app
from datetime import datetime

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
    except Exception as e:
        print(f"{e}")

    current_user = cur.fetchone()

    return current_user

def get_counterparties() -> tuple:
    db = get_db()
    cur = db.cursor()
    error = None

    try:
        cur.execute("""
                SELECT 
                    counterparties.id,
                    counterparties.name
                FROM 
                    counterparties""")
    except Exception as e:
        print(f"{e}")

    counterparties = cur.fetchall()

    return counterparties

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
    # app.cli.add_command(create_super_user)