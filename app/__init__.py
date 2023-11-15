import os
from flask import Flask, render_template
from app.db import db
from app.db_config import db_config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


# LoginManager
from flask_login import LoginManager, login_required
from app.resources.bonita import get_completed_tasks_by_name, get_ready_tasks, get_bonita_variable

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
    
    from app.models.collection import Coleccion
    from app.models.user import User
    from app.models.material import Material
    from app.models.model import Modelo
    from app.models.tipo import Tipo
    from app.models.tarea import Tarea
    from app.models.coleccion_sede import Coleccion_sede
    from app.models.sede import Sede

    
    with app.app_context():
        db.create_all()

    # LoginManager Config
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicie sesion para acceder a este sitio"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    app.jinja_env.globals.update(
        get_ready_tasks=get_ready_tasks,
        get_completed_tasks_by_name=get_completed_tasks_by_name,
        get_bonita_variable=get_bonita_variable,
    )

    
    @app.route("/")
    @login_required
    def home():
        return render_template("home.html")
    
    from app.resources import collection, auth, reserve, type, tarea
    from app.resources.model import model
    
    app.register_blueprint(collection.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(model.bp)
    app.register_blueprint(type.bp)
    
    return app

