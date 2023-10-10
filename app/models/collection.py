from datetime import datetime
from app.db import db

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    plazo_fabricacion = db.Column(db.String(50), nullable=False)
    fecha_lanzamiento_estimada = db.Column(db.Date, nullable=False, default=datetime.now)


    def __init__(self,id, nombre, descripcion, plazo_fabricacion, fecha_lanzamiento_estimada):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.plazo_fabricacion = plazo_fabricacion
        self.fecha_lanzamiento_estimada = fecha_lanzamiento_estimada