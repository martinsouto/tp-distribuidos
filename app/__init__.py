import os
from flask import Flask
from app.resources import collection

def create_app():
    app = Flask(__name__)

    # Configura una clave secreta
    app.config['SECRET_KEY'] = 'dssd'  # Reemplaza 'tu_clave_secreta_aqui' por una clave secreta real y segura

    @app.route("/")
    def hello_world():
        return "<p>Hello, Braian!</p>"
    
    app.register_blueprint(collection.bp)
    
    return app
