import os
from flask import Flask
from app.resources import collection

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
    )

    @app.route("/")
    def hello_world():
        return "<p>Hello, Braian!</p>"
    
    app.register_blueprint(collection.bp)
    
    return app