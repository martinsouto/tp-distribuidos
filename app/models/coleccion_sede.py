from app.db import db

# Login
from flask_login import UserMixin


class Coleccion_sede(db.Model, UserMixin):
    __tablename__ = "coleccion_sede"

    id = db.Column(db.Integer, primary_key=True)
    id_coleccion = db.Column(db.Integer, db.ForeignKey("coleccion.id"), nullable=False)
    id_sede = db.Column(db.Integer, db.ForeignKey("sede.id"), nullable=False)
    cantidad_lotes = db.Column(db.Integer)
    entregado = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        id_coleccion,
        id_sede,
        cantidad_lotes,
        entregado,
    ):
        self.id_coleccion = id_coleccion
        self.id_sede = id_sede
        self.cantidad_lotes = cantidad_lotes
        self.entregado = entregado

    def crear(id_coleccion, id_sede, cantidad_lotes, entregado):
        """Crea una relación entre una colección y una sede"""
        sede = Coleccion_sede(id_coleccion, id_sede, cantidad_lotes, entregado)
        db.session.add(sede)
        db.session.commit()

    def get_by_id_coleccion(id_coleccion):
        """Devuelve todas las sedes de una colección"""
        return Coleccion_sede.query.filter_by(id_coleccion=id_coleccion).all()

    def get_by_id(id):
        """Devuelve una entrega por su id"""
        return Coleccion_sede.query.filter_by(id=id).first()

    def estado(self):
        """Devuelve el estado de la entrega"""
        if self.entregado:
            return "Enviado"
        else:
            return "Pendiente de envío"

    def enviar(self):
        """Envía la entrega"""
        self.entregado = True
        db.session.commit()

    def lotes_enviados(id_coleccion):
        """Devuelve True si todos los lotes de una colección fueron enviados"""
        lotes = Coleccion_sede.query.filter_by(id_coleccion=id_coleccion, entregado=False).all()
        return len(lotes) == 0

    def eliminar(id_coleccion):
        """Elimina todas las entregas de una colección"""
        lista = Coleccion_sede.query.filter_by(id_coleccion=id_coleccion).all()
        for l in lista:
            db.session.delete(l)
            db.session.commit()
