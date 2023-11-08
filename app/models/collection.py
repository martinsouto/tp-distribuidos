from app.db import db

# Login
from flask_login import UserMixin

from app.models.model import Modelo
from app.models.user import User
from sqlalchemy import text

coleccion_tiene_modelo = db.Table(
    "coleccion_tiene_modelo",
    db.Column(
        "coleccion_id", db.Integer, db.ForeignKey("coleccion.id"), primary_key=True
    ),
    db.Column(
        "modelo_id",
        db.Integer,
        db.ForeignKey("modelo.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

coleccion_tiene_usuario = db.Table(
    "coleccion_tiene_usuario",
    db.Column(
        "coleccion_id", db.Integer, db.ForeignKey("coleccion.id"), primary_key=True
    ),
    db.Column(
        "usuario_id",
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Coleccion(db.Model, UserMixin):
    __tablename__ = "coleccion"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer)
    name = db.Column(db.String(255), unique=True)
    cantidad_muebles = db.Column(db.Integer)
    fecha_lanzamiento = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)
    materiales = db.Column(db.String(255), nullable=True)
    tareas = db.relationship("Tarea", backref="coleccion", uselist=True)
    inicio_fabricacion = db.Column(db.DateTime, nullable=True)
    fin_fabricacion = db.Column(db.DateTime, nullable=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    coleccion_sede = db.relationship(
        "Coleccion_sede", backref="coleccion", uselist=False
    )

    # relacion Many-to-Many
    coleccion_tiene_modelo = db.relationship(
        "Modelo",
        secondary=coleccion_tiene_modelo,
        lazy="subquery",
        backref=db.backref("colecciones", lazy=True),
    )

    coleccion_tiene_usuario = db.relationship(
        "User",
        secondary=coleccion_tiene_usuario,
        lazy="subquery",
        backref=db.backref("colecciones", lazy=True),
    )

    def __init__(
        self,
        case_id,
        name,
        cantidad_muebles,
        fecha_lanzamiento,
        fecha_entrega,
        usuarios,
        modelos,
    ):
        self.case_id = case_id
        self.name = name
        self.cantidad_muebles = cantidad_muebles
        self.fecha_lanzamiento = fecha_lanzamiento
        self.fecha_entrega = fecha_entrega
        lista = []
        for usuario_id in usuarios:
            lista.append(User.query.get(usuario_id))
        self.coleccion_tiene_usuario = lista
        lista = []
        for modelo_id in modelos:
            lista.append(Modelo.query.get(modelo_id))
        self.coleccion_tiene_modelo = lista

    def crear(
        case_id,
        name,
        cantidad_muebles,
        fecha_lanzamiento,
        fecha_entrega,
        usuarios,
        modelos,
    ):
        """Crea una coleccion"""
        coleccion = Coleccion(
            case_id,
            name,
            cantidad_muebles,
            fecha_lanzamiento,
            fecha_entrega,
            usuarios,
            modelos,
        )
        db.session.add(coleccion)
        db.session.commit()

    def get_by_name(name):
        return Coleccion.query.filter_by(name=name).first()

    def get_by_id(id):
        return Coleccion.query.filter_by(id=id).first()

    def save_materials(self, materiales):
        """Guarda la lista temporal de materiales a reservar"""
        self.materiales = materiales
        db.session.commit()

    def delete_materials(self):
        """Borra la lista temporal de materiales a reservar"""
        self.materiales = ""
        db.session.commit()

    def save_espacio_fabricacion(self, inicio, fin):
        """Guarda las fechas del espacio de fabricación reservado"""
        self.inicio_fabricacion = inicio
        self.fin_fabricacion = fin
        db.session.commit()

    def modificar_lanzamiento(self, nueva_fecha):
        """Modifica la fecha de lanzamiento de la coleccion"""
        self.fecha_lanzamiento = nueva_fecha
        db.session.commit()

    def modificar_entrega(self, nueva_fecha):
        """Modifica la fecha de entrega de la coleccion"""
        self.fecha_entrega = nueva_fecha
        db.session.commit()

    def get_all_colections():
        return Coleccion.query.all()

    def get_most_used_model():
        query = db.engine.execute(
            text(
                "SELECT modelo_id, COUNT(modelo_id) as total FROM coleccion_tiene_modelo GROUP BY modelo_id ORDER BY total desc LIMIT 1"
            )
        )
        modelo_id = [row[0] for row in query][0]
        modelo = Modelo.get_by_id(modelo_id)
        return modelo

    def get_cant_most_used_model():
        query = db.engine.execute(
            text(
                "SELECT COUNT(modelo_id) as total FROM coleccion_tiene_modelo GROUP BY modelo_id ORDER BY total desc LIMIT 1"
            )
        )
        cant = [row[0] for row in query][0]
        return cant

    def eliminar(id_coleccion):
        """elimina la coleccion"""
        coleccion = Coleccion.get_by_id(id_coleccion)
        print(coleccion)
        db.session.delete(coleccion)
        db.session.commit()
