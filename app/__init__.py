import os
from flask import Flask, render_template
from app.db import db
from app.db_config import db_config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_config.get('USER')}:{db_config.get('PASSWORD')}@{db_config.get('HOST')}/{db_config.get('DATABASE')}"

    app.config.from_mapping(
        SECRET_KEY='mikey',
        DATABASE_HOST=db_config.get("HOST"),
        DATABASE_USER=db_config.get("USER"),
        DATABASE_PASSWORD=db_config.get("PASSWORD"),
        DATABASE=db_config.get("DATABASE"),
    )

    #from app import db
    #db = SQLAlchemy()
    db.init_app(app)
    
    from app.models.collection import Collection
    
    with app.app_context():
        db.create_all()

    @app.route("/")
    def hello_world():
        return "<p>Hello, Braian!</p>"
    
    from app.resources import collection
    
    app.register_blueprint(collection.bp)

    
    return app

