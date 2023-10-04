from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length
from datetime import date

class FormAltaColeccion(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El campo nombre es obligatorio"),
            Length(min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"),
        ],
        default="",
    )

    descripcion = TextAreaField(
        "Descripción",
        validators=[
            DataRequired(message="El campo descripción es obligatorio"),
            Length(
                min=10, max=200, message="El mínimo de caracteres es 10 y el máximo 200"
            ),
        ],
        default="",
    )

    plazo_fabricacion = StringField(
        "Plazo de Fabricación",
        validators=[
            DataRequired(message="El campo plazo de fabricación es obligatorio"),
            Length(
                min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
            ),
        ],
        default="",
    )

    fecha_lanzamiento_estimada = DateField(
        "Fecha de Lanzamiento Estimada",
        validators=[DataRequired(message="El campo fecha de lanzamiento es obligatorio")],
        default=date.today(),
    )

    enviar = SubmitField("Create")
