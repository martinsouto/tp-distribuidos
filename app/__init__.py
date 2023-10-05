import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.resources import collection
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SQLAlchemy()  

def create_app():
    app = Flask(__name__)

    # Configura una clave secreta
    app.config['SECRET_KEY'] = 'dssd'  # Reemplaza 'tu_clave_secreta_aqui' por una clave secreta real y segura

    # BD
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/probando2'

    # inicializo
    db.init_app(app)

    from app.models.coleccion import Coleccion

    print("Antes de crear las tablas en la base de datos")  # Agrega esta línea
    with app.app_context():
        db.create_all()
    print("Después de crear las tablas en la base de datos")  # Agrega esta línea


    @app.route("/")
    def hello_world():
        return "<p>Hello, Braian!</p>"
    
    app.register_blueprint(collection.bp)

    
    return app