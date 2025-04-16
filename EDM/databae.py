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

    with current_app.open_resource('schema.sql') as f:
        cur = db.cursor()
        cur.execute(f.read().decode('utf8'))
        db.commit()


@click.command('init-db')
def init_db_command():
    """ Команда для cli для инициализации базы данных. """
    init_db()
    click.echo("Successfully initialized the database.")

@click.command('create-super-user')
@click.argument('login')
@click.argument('password')
def create_super_user(login: str, password: str):
    """  Команда для cli для создания суперпользователя. """
    db = get_db()

    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (role, blocked, login, email, password_digest, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            ('admin', False, login, 'admin_email', generate_password_hash(password), datetime.now()))
    except psycopg2.errors.UniqueViolation:
        click.echo("User with this login already exists.")
    except psycopg2.Error as e:
        click.echo(f"Error: {e}")
    else:
        db.commit()
        click.echo("Successfully created superuser.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_super_user)