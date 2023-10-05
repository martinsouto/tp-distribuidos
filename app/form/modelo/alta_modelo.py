from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from datetime import date

class FormAltaModelo(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El campo nombre es obligatorio"),
            Length(min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"),
        ],
        default="",
    )

    tipo = SelectField('Tipo', choices=[('cocina', 'Cocina'), ('escritorio', 'Escritorio'), ('comedor', 'Comedor'), ('dormitorio','Dormitorio'),('baño','Baño'),('exterior','Exterior')],
                           validators=[DataRequired()])
