import datetime
from pipes import quote
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.coleccion.reprogramar_coleccion import FormReprogramarColeccion
from app.form.modelo.alta_modelo import FormAltaModelo
from app.form.tarea.alta_tarea import FormAltaTarea
from app.models.collection import Coleccion
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
import json  # Importa la biblioteca json
import requests
from app.models.sede import Sede  # Importa la biblioteca requests
from app.models.tarea import Tarea
from app.resources.auth import login_required
from app.resources.bonita import *
from app.models.coleccion_sede import Coleccion_sede
from datetime import timedelta
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
            while "Seleccionar fecha de lanzamiento" not in get_ready_tasks(case_id):
                print("Cargando...")
            # Se asigna la tarea 'Seleccionar fecha de lanzamiento'
            taskId = getUserTaskByName("Seleccionar fecha de lanzamiento", case_id)
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            # Si todo salió bien se crea la colección
            # resto 10 días para setear fecha entrega y mando vacio para los modelos
            Coleccion.crear(
                case_id,
                nombre,
                form.cantidad_muebles.data,
                fecha_lanzamiento,
                fecha_lanzamiento - datetime.timedelta(10),
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

@bp.route('/<int:id_coleccion>/planificar', methods=['GET'])
@login_required
def planificar_fabricacion(id_coleccion):
    """Planificación de la fabricación de una coleccion"""
    form = FormAltaTarea()
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        tareas = Tarea.get_by_coleccion_id(id_coleccion)
        return render_template(
            "collection/planificar_fabricacion.html",
            coleccion=coleccion,
            tareas=tareas,
            form=form,
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/elaborar_plan', methods=['GET', 'POST'])
@login_required
def elaborar_plan(id_coleccion):
    """Elaboración del plan de fabricación de una coleccion"""
    if session["current_rol"] == "Operaciones":
        tareas = Coleccion.get_by_id(id_coleccion).tareas
        print(tareas)
        taskId = getUserTaskByName(
            "Elaborar plan de fabricacion",
            Coleccion.get_by_id(id_coleccion).case_id,
        )
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
        flash("Planificación creada!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    #return redirect(url_for("home"))
    coleccion = Coleccion.get_by_id(id_coleccion)
    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    return render_template(
            "collection/administrar_tareas.html", coleccion=coleccion, tareas=tareas
        )

@bp.route('/<int:id_coleccion>/administrar_tareas', methods=['GET'])
@login_required
def administrar_tareas(id_coleccion):
    """Administración de las tareas de una coleccion"""
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        tareas = Tarea.get_by_coleccion_id(id_coleccion)
        return render_template(
            "collection/administrar_tareas.html", coleccion=coleccion, tareas=tareas
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/eliminar_coleccion', methods=['GET', 'DELETE'])
@login_required
def eliminar_coleccion(id_coleccion):
    """Eliminación de una coleccion"""
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        deleteCase(coleccion.case_id)
        Coleccion_sede.eliminar(id_coleccion)
        Tarea.eliminar_todas(id_coleccion)
        Coleccion.eliminar(id_coleccion)
        print("pase")
        flash("Colección eliminada exitosamente", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/nueva_distribucion', methods=['GET'])
@login_required
def nueva_distribucion(id_coleccion):
    """Planificación de la distribución de una coleccion"""
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        sedes = Sede.sedes()
        return render_template(
            "collection/planificar_distribucion.html",
            coleccion=coleccion,
            sedes=sedes,
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/planificar_distribucion', methods=['GET','POST'])
@login_required
def planificar_distribucion(id_coleccion):
    """Planificación de la distribución de una coleccion"""
    if session["current_rol"] == "Operaciones":
        cantidades = request.form.getlist("cantidades[]")
        coleccion = Coleccion.get_by_id(id_coleccion)
        cant = 0
        for c in cantidades:
            cant = cant + int(c)
        if cant <= coleccion.cantidad_muebles:
            taskId = getUserTaskByName(
                "Iniciar planificacion de distribucion",
                coleccion.case_id,
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            for index, c in enumerate(cantidades):
                if int(c) > 0:
                    Coleccion_sede.crear(id_coleccion, index + 1, c, False)
            flash("La distribución se planificó con éxito", "success")
            lotes = Coleccion_sede.get_by_id_coleccion(id_coleccion)
            return render_template(
                "collection/ver_lotes.html",
                coleccion=coleccion,
                lotes=lotes,
                )
        else:
            sedes = Sede.sedes()
            flash(
                "No se cuenta con la cantidad de muebles suficientes para distribuir",
                "error",
            )
            return render_template(
                "collection/planificar_distribucion.html",
                coleccion=coleccion,
                sedes=sedes,
            )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/ver_lotes', methods=['GET'])
@login_required
def ver_lotes(id_coleccion):
    """Visualización de los lotes de una coleccion"""
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        lotes = Coleccion_sede.get_by_id_coleccion(id_coleccion)
        return render_template(
            "collection/ver_lotes.html",
            coleccion=coleccion,
            lotes=lotes,
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_lote>/enviar_lote', methods=['GET','POST'])
@login_required
def enviar_lote(id_lote):
    """Envío de un lote de una coleccion"""
    lote = Coleccion_sede.get_by_id(id_lote)
    coleccion = Coleccion.get_by_id(lote.id_coleccion)
    if session["current_rol"] == "Operaciones":
        #obtengo la variable de bonita coleccion_finalizada. Si es true, no se puede enviar
        if get_bonita_variable(coleccion.case_id, "coleccion_finalizada") != "true":
            flash("No se puede enviar el lote porque la colección aún no finalizó", "error")
        else:
            lote.enviar()
            if Coleccion_sede.lotes_enviados(coleccion.id):
                taskId = getUserTaskByName(
                    "Asociar lotes con las ordenes de distribucion",
                    coleccion.case_id,
                )
                assign_task(taskId)
                # Se finaliza la tarea
                updateUserTask(taskId, "completed")
                flash("Lotes enviados!", "success")
                return redirect(url_for("home"))
            else:
                flash("Se realizo el envío con éxito", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    lotes = Coleccion_sede.get_by_id_coleccion(lote.id_coleccion)
    return render_template(
        "collection/ver_lotes.html",
        coleccion=coleccion,
        lotes=lotes,
    )

@bp.route('/<int:id_coleccion>/reprogramar', methods=['POST'])
@login_required
def reprogramar(id_coleccion):
    """Reprogramación de una coleccion"""
    if session["current_rol"] == "Operaciones":
        form = FormReprogramarColeccion()
        coleccion = Coleccion.get_by_id(id_coleccion)
        form.fecha_lanzamiento.data = coleccion.fecha_lanzamiento
        return render_template(
            "collection/reprogramar.html", coleccion=coleccion, form=form
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/modificar_fecha', methods=['POST'])
@login_required
def modificar_fecha(id_coleccion):
    """Modificación de la fecha de lanzamiento de una coleccion"""
    if session["current_rol"] == "Operaciones":
        form = FormReprogramarColeccion()
        coleccion = Coleccion.get_by_id(id_coleccion)
        if form.validate_on_submit():
            nueva_fecha = form.fecha_lanzamiento.data
            coleccion.modificar_lanzamiento(nueva_fecha)
            while "Seleccionar fecha de lanzamiento" not in get_ready_tasks(
                coleccion.case_id
            ):
                print("Cargando SELECCIONAR FECHA...")
            taskId = getUserTaskByName(
                "Seleccionar fecha de lanzamiento", coleccion.case_id
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            coleccion.modificar_entrega(coleccion.fecha_lanzamiento - timedelta(10))
            set_bonita_variable(
                coleccion.case_id, "reprogramar_lanzamiento", "false", "java.lang.Boolean"
            )
            flash("Colección reprogramada con éxito!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))