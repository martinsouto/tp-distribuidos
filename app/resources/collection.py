import datetime
from pipes import quote
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.coleccion.reprogramar_coleccion import FormReprogramarColeccion
from app.form.modelo.alta_modelo import FormAltaModelo
from app.form.hito.alta_hito import FormAltaHito
from app.models.collection import Coleccion
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
import json  # Importa la biblioteca json
import requests
from app.models.sede import Sede  # Importa la biblioteca requests
from app.models.hito import Hito
from app.resources.auth import login_required
from app.resources.bonita import *
from app.models.coleccion_sede import Coleccion_sede
from datetime import timedelta
from app.models.model import Modelo
from app.models.hito import Hito


bp = Blueprint('collection', __name__, url_prefix="/collection")

@bp.route('/create', methods=['POST','GET'])
@login_required
def crear():
    """Creación de una nueva coleccion"""
    if session["current_rol"] == "Creativa":
        form = FormAltaColeccion()
        if form.validate_on_submit():
            nombre = form.nombre.data
            fecha_lanzamiento = form.fecha_lanzamiento.data
            #modelos = request.form.getlist("modelos[]")
            cant_modelos = request.form.getlist("cant_modelos[]")
            print("#############################################################################################################################################")
            modelos_todos = Modelo.modelos()
            cant_muebles = 0
            modelos = []
            for i in range(len(cant_modelos)):
                if int(cant_modelos[i]) > 0:
                    cant_muebles += int(cant_modelos[i])
                    modelos.append(str(i+1))
            if (cant_muebles == 0):
                flash("Debes incluir al menos un modelo", "error")
                modelos = Modelo.modelos()
                return render_template("collection/nuevo.html", form=form, modelos=modelos)
            print("#############################################################################################################################################")
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
            print("SE REALIZO LA SELECCION DE FECHA DE LANZAMIENTO")
            # Si todo salió bien se crea la colección
            # resto 10 días para setear fecha entrega y mando vacio para los modelos
            Coleccion.crear(
                case_id,
                nombre,
                cant_muebles,
                fecha_lanzamiento,
                fecha_lanzamiento - datetime.timedelta(10),
                [1, 2, 3],
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
    form = FormAltaHito()
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        hitos = Hito.get_by_coleccion_id(id_coleccion)
        return render_template(
            "collection/planificar_fabricacion.html",
            coleccion=coleccion,
            hitos=hitos,
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
        hitos = Coleccion.get_by_id(id_coleccion).hitos
        print(hitos)
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
    hitos = Hito.get_by_coleccion_id(id_coleccion)
    return render_template(
            "collection/administrar_hitos.html", coleccion=coleccion, hitos=hitos
        )

@bp.route('/<int:id_coleccion>/administrar_hitos', methods=['GET'])
@login_required
def administrar_hitos(id_coleccion):
    """Administración de los hitos de una coleccion"""
    if session["current_rol"] == "Operaciones":
        coleccion = Coleccion.get_by_id(id_coleccion)
        hitos = Hito.get_by_coleccion_id(id_coleccion)
        return render_template(
            "collection/administrar_hitos.html", coleccion=coleccion, hitos=hitos
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
        Hito.eliminar_todas(id_coleccion)
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
    if session["current_rol"] == "Comercial":
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
    if session["current_rol"] == "Comercial":
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
    if session["current_rol"] == "Comercial":
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
    if session["current_rol"] == "Comercial":
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
    if session["current_rol"] == "Creativa":
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
    if session["current_rol"] == "Creativa":
        form = FormReprogramarColeccion()
        coleccion = Coleccion.get_by_id(id_coleccion)
        if form.validate_on_submit():
            # Si reprogramo porque no hay materiales
            if "Consulta de Disponibilidad de Materiales" in get_ready_tasks(coleccion.case_id):
                print("REPROGRAMANDO XQ NO HAY MATERIALES")
                taskId = getUserTaskByName(
                    "Consulta de Disponibilidad de Materiales",
                    Coleccion.get_by_id(id_coleccion).case_id,
                )
                assign_task(taskId)
                # Se finaliza la tarea
                updateUserTask(taskId, "completed")
                # La variable materiales_fecha es false por lo que se vuelve al inicio

            # Si reprogramo porque no hay espacios
            elif "Consulta de espacio de fabricacion" in get_ready_tasks(
                coleccion.case_id
            ):
                print("REPROGRAMANDO XQ NO HAY ESPACIOS")
                taskId = getUserTaskByName(
                    "Consulta de espacio de fabricacion",
                    Coleccion.get_by_id(id_coleccion).case_id,
                )
                assign_task(taskId)
                # Se finaliza la tarea
                updateUserTask(taskId, "completed")
                # La variable plazos_fabricacion es false por lo que se vuelve al inicio

            # Si reprogramo porque no llegaron los materiales
            elif "Esperar materiales" in get_ready_tasks(coleccion.case_id):
                print("REPROGRAMANDO XQ NO LLEGARON LOS MATERIALES")
                # Seteo la variable de bonita materiales_atrasados en false
                set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "materiales_atrasados", "true", "java.lang.Boolean"
                )
                set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "materiales_disponibles", "true", "java.lang.Boolean"
                )
                taskId = getUserTaskByName(
                    "Esperar materiales",
                    Coleccion.get_by_id(id_coleccion).case_id,
                )
                assign_task(taskId)
                # Se finaliza la tarea
                updateUserTask(taskId, "completed")
                #espero a que se complete la tarea, y que lance la tarea de seleccionar fecha de lanzamiento para poner materiales_disponibles en false
                while "Seleccionar fecha de lanzamiento" not in get_ready_tasks(coleccion.case_id):
                    print("ESPERANDO SELECCIONAR FECHA...")
                #ahora ya puedo volver a poner materiales_disponibles en false
                set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "materiales_disponibles", "false", "java.lang.Boolean"
                )
            # Si reprogramo porque que los hitos no se completan a tiempo
            elif get_completed_tasks_by_name(coleccion.case_id, "Elaborar plan de fabricacion") and "Asociar lotes con las ordenes de distribucion" not in get_ready_tasks(coleccion.case_id) and not get_completed_tasks_by_name(coleccion.case_id, "Asociar lotes con las ordenes de distribucion"):
                print("REPROGRAMANDO XQ NO SE FABRICÓ A TIEMPO")
                set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "reprogramar_lanzamiento", "true", "java.lang.Boolean"
                )
                set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "hitos_cumplidos", "true", "java.lang.Boolean"
                )
                taskId = getUserTaskByName(
                    "Esperar finalizar hitos",
                    Coleccion.get_by_id(id_coleccion).case_id,
                )
                assign_task(taskId)
                # Se finaliza la tarea
                updateUserTask(taskId, "completed")
                Hito.eliminar_todas(id_coleccion)
                # Elimino todas las tareas de la colección
                #espero a que se complete la tarea, y que lance la tarea de seleccionar fecha de lanzamiento para poner hitos_cumplidos en false
                while "Seleccionar fecha de lanzamiento" not in get_ready_tasks(coleccion.case_id):
                    print("ESPERANDO SELECCIONAR FECHA...")
                #ahora ya puedo volver a poner materiales_disponibles en false
                set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "hitos_cumplidos", "false", "java.lang.Boolean"
                )
            else:
                flash("No se puede reprogramar en este momento", "error")
                return redirect(url_for("home"))
            
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
            #seteo sedes_disponibles en false para que reserve nuevamente
            set_bonita_variable(
                coleccion.case_id, "sedes_disponibles", "false", "java.lang.Boolean"
            )
            flash("Colección reprogramada con éxito!", "success")
        else:
            return render_template(
                "coleccion/reprogramar.html", coleccion=coleccion, form=form
            )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))