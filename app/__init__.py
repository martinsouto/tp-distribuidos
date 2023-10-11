import os
from flask import Flask, render_template
from app.db import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.environ.get('FLASK_DATABASE_USER')}:{os.environ.get('FLASK_DATABASE_PASSWORD')}@{os.environ.get('FLASK_DATABASE_HOST')}/{os.environ.get('FLASK_DATABASE')}"

    app.config.from_mapping(
        SECRET_KEY='mikey',
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_USER=os.environ.get('FLASK_DATABASE_USER'),
        DATABASE_PASSWORD=os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE=os.environ.get('FLASK_DATABASE'),
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

