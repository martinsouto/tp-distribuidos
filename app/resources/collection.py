import datetime
from pipes import quote
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.modelo.alta_modelo import FormAltaModelo
from app.models.collection import Collection
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
import json  # Importa la biblioteca json
import requests  # Importa la biblioteca requests
from app.resources.auth import login_required
from app.resources.bonita import *


bp = Blueprint('collection', __name__, url_prefix="/collection")

@bp.route('/create', methods=['POST','GET'])
@login_required
def create():
    """Creación de una nueva coleccion"""
    form = FormAltaColeccion()
    if request.method == 'POST':
        if request.form.get('next'):
            form = FormAltaModelo()
            return render_template('model/create.html', form=form)
        if request.form.get('create'):
            form = FormAltaColeccion()
            #response = loginBonita();
            nombre = form.nombre.data
            #por ahora no hacemos nada con los datos del formulario por que no tenemos modelos
            # Se instancia la tarea
            case_id = init_process()
            # Obtengo id de tarea
            taskId = getUserTaskByName("Planificar la coleccion", case_id)
            # Se le asigna la tarea al usuario que creó la colección
            #Coleccion.create(
            #        nombre coleccion,
            #        "descripcion coleccion",
            #        "plazo de fabricacion",
            #        datetime.now(),
            #    )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            # Seteo variable en bonita, hardcodeo el id de la colección xq aún no tenemos modelo
            set_bonita_variable(case_id, "coleccion_id", 1, "java.lang.Integer")
            flash("¡La colección fue creada con exito!")
            return render_template('collection/create.html', form=form)
            #return redirect(url_for("home"))
    # Si el formulario no se ha enviado o hay errores de validación,
    # simplemente muestra el formulario nuevamente
    return render_template('collection/create.html', form=form)
