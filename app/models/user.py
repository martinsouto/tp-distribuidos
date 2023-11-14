from datetime import datetime
from app.db import db
# Login
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(102), nullable=False)

    @classmethod
    def find_by_username(cls, username):
        """Devuelve un usuario por su username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, id):
        """Devuelve un usuario por su id"""
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def create(cls, user):
        """Crea un usuario"""
        db.session.add(user)
        db.session.commit()