import datetime
from pipes import quote
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.modelo.alta_modelo import FormAltaModelo
from app.models.collection import Coleccion
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
import json  # Importa la biblioteca json
import requests
from app.models.sede import Sede  # Importa la biblioteca requests
from app.resources.auth import login_required
from app.resources.bonita import *

from app.models.model import Modelo


bp = Blueprint('collection', __name__, url_prefix="/collection")

@bp.route('/create', methods=['POST','GET'])
@login_required
def crear():
    """Creación de una nueva coleccion"""
    if session["current_rol"] == "Operaciones":
        form = FormAltaColeccion()
        if form.validate_on_submit():
            nombre = form.nombre.data
            fecha_lanzamiento = form.fecha_lanzamiento.data
            modelos = request.form.getlist("modelos[]")
            # Se instancia la tarea
            case_id = init_process()
            while "Planificar la coleccion" not in get_ready_tasks(case_id):
                print("Cargando... (planificar coleccion)")
            taskId = getUserTaskByName("Planificar la coleccion", case_id)
            # Se le asigna la tarea al usuario que creó la colección
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            # Si todo salió bien se crea la colección
            # resto un mes para setear fecha entrega y mando vacio para los modelos
            Coleccion.crear(
                case_id,
                nombre,
                form.cantidad_muebles.data,
                fecha_lanzamiento,
                fecha_lanzamiento - datetime.timedelta(30),
                [1],
                modelos,
            )
            # Cargar las variables en bonita
            coleccion = Coleccion.get_by_name(nombre)

            set_bonita_variable(
                case_id, "materiales_disponibles", "false", "java.lang.Boolean"
            )
            set_bonita_variable(
                case_id, "coleccion_id", coleccion.id, "java.lang.Integer"
            )

            flash("¡La colección fue creada con exito!", "success")
            return redirect(url_for("home"))
        else:
            modelos = Modelo.modelos()
            return render_template("collection/nuevo.html", form=form, modelos=modelos)
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))