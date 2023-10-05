from datetime import datetime
from app.__init__ import db

class Coleccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    plazo_fabricacion = db.Column(db.String(50), nullable=False)
    fecha_lanzamiento_estimada = db.Column(db.Date, nullable=False, default=datetime.now)

    