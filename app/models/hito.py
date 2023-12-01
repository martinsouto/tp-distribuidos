from app.db import db

# Login
from flask_login import UserMixin


class Hito(db.Model, UserMixin):
    __tablename__ = "hito"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True)
    descripcion = db.Column(db.String(255))
    fecha_limite = db.Column(db.DateTime)
    coleccion_id = db.Column(db.Integer, db.ForeignKey("coleccion.id"), nullable=False)
    finalizada = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        nombre,
        descripcion,
        fecha_limite,
        coleccion_id,
    ):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.coleccion_id = (coleccion_id,)
        self.finalizada = False

    def crear(nombre, descripcion, fecha_limite, coleccion_id):
        """Crea un hito"""
        hito = Hito(nombre, descripcion, fecha_limite, coleccion_id)
        db.session.add(hito)
        db.session.commit()

    def eliminar(self):
        """Elimina un hito"""
        db.session.delete(self)
        db.session.commit()

    def finalizar(self):
        """Elimina un hito"""
        self.finalizada = True
        db.session.commit()

    def hitos():
        """Devuelve todos los hitos"""
        return Hito.query.all()

    def get_by_name(nombre):
        """Devuelve un hito por su nombre"""
        return Hito.query.filter_by(nombre=nombre).first()

    def get_by_name_and_coleccion(nombre, coleccion_id):
        """Devuelve un hito por su nombre y coleccion_id"""
        return Hito.query.filter_by(nombre=nombre, coleccion_id=coleccion_id).first()

    def get_by_id(id):
        """Devuelve un hito por su id"""
        return Hito.query.filter_by(id=id).first()

    def get_by_coleccion_id(coleccion_id):
        """Devuelve un hito por su coleccion_id"""
        return Hito.query.filter_by(coleccion_id=coleccion_id).all()

    def coleccion_finalizada(id_coleccion):
        """Devuelve True si todos los hitos de una coleccion estan finalizadas"""
        hitos = Hito.query.filter_by(coleccion_id=id_coleccion, finalizada=False).all()
        return len(hitos) == 0

    def eliminar_todas(coleccion_id):
        """Elimina todas los hitos de una coleccion"""
        lista = Hito.query.filter_by(coleccion_id=coleccion_id).all()
        for l in lista:
            db.session.delete(l)
            db.session.commit()
