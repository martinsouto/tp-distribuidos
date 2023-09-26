import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
    )

    @app.route("/")
    def hello_world():
        return "<p>Hello, Braian!</p>"
    
    return app