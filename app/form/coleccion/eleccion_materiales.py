from flask_wtf import FlaskForm
from wtforms import DateField, SelectMultipleField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from datetime import date


class FormEleccionMateriales(FlaskForm):
    fecha_entrega = DateField(
        "Fecha recepción de materialess",
        default=date.today,
        validators=[DataRequired(message="El campo para la fecha de recepción es obligatorio")],
    )

    enviar = SubmitField("Guardar")

    def validate_fecha_entrega(self, field):
        if field.data <= date.today():
            raise ValidationError(
                "La fecha de recepción de materiales debe ser posterior a la fecha actual"
            )