import os
from flask import Flask
from app.resources import collection
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)

    # Configura una clave secreta
    app.config['SECRET_KEY'] = 'dssd'  # Reemplaza 'tu_clave_secreta_aqui' por una clave secreta real y segura

    # BD
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/dssd'
    db = SQLAlchemy(app)

    @app.route("/")
    def hello_world():
        return "<p>Hello, Braian!</p>"
    
    app.register_blueprint(collection.bp)
    
    return app
