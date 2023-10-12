import mysql.connector
import click
from app.db_config import db_config
from flask import current_app, g
from flask.cli import with_appcontext
from .schema import instructions

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=db_config.get("HOST"),
            user=db_config.get("USER"),
            password=db_config.get("PASSWORD"),
            database=db_config.get("DATABASE"),
        )
        g.c = g.db.cursor(dictionary=True)
    return g.db, g.c

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db, c = get_db()
    for i in instructions:
        c.execute(i)
    db.commit()

@click.command('init-db') #to create the database's tables the command is: flask init-db
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Database initialized')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

################################################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)