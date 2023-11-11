import time
from flask import (
    redirect, render_template, url_for, flash, session, request, Blueprint
)
from flask_login import login_required, current_user
from app.models.tarea import Tarea
from app.models.collection import Coleccion
from app.form.tarea.alta_tarea import FormAltaTarea
from datetime import datetime
from app.resources.bonita import set_bonita_variable
from app.resources.collection import bp
#REFACTORIZADO
@bp.route('/<int:id_coleccion>/crear_tarea', methods=['POST'])
@login_required
def crear_tarea(id_coleccion):
    coleccion = Coleccion.get_by_id(id_coleccion)
    if session["current_rol"] != "Operaciones":
        flash("No tienes permiso para acceder a este sitio", "error")
        return redirect(url_for("home"))

    form = FormAltaTarea()
    form.fin_fabricacion = coleccion.fin_fabricacion
    form.id_coleccion = id_coleccion

    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        fecha_limite = form.fecha_limite.data
        Tarea.crear(nombre, descripcion, fecha_limite, id_coleccion)
        flash("Tarea creada", "success")
    else:
        flash("Hay errores en los campos de la tarea", "error")

    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    return render_template(
        "collection/planificar_fabricacion.html", coleccion=coleccion, tareas=tareas, form=form
    )

@bp.route('/<int:id_coleccion>/<int:id_tarea>/eliminar', methods=['GET', 'DELETE'])
@login_required
def eliminar_tarea(id_coleccion, id_tarea):
    if session["current_rol"] != "Operaciones":
        flash("No tienes permiso para acceder a este sitio", "error")
        return redirect(url_for("home"))

    tarea = Tarea.get_by_id(id_tarea)
    tarea.eliminar()
    flash("Tarea eliminada", "success")

    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    form = FormAltaTarea()
    return render_template(
        "collection/planificar_fabricacion.html", coleccion=Coleccion.get_by_id(id_coleccion), tareas=tareas, form=form
    )

@bp.route('/<int:id_coleccion>/<int:id_tarea>/finalizar', methods=['GET','POST'])
@login_required
def finalizar_tarea(id_coleccion, id_tarea):
    if session["current_rol"] != "Operaciones":
        flash("No tienes permiso para acceder a este sitio", "error")
        return redirect(url_for("home"))

    tarea = Tarea.get_by_id(id_tarea)
    tarea.finalizar()

    if Tarea.coleccion_finalizada(id_coleccion):
        coleccion = Coleccion.get_by_id(id_coleccion)
        set_bonita_variable(coleccion.case_id, "hitos_cumplidos", "true", "java.lang.Boolean")
        #Hay que ver si es necesario poner esta variable en True en este momento
        #set_bonita_variable(coleccion.case_id, "coleccion_fabricada", "true", "java.lang.Boolean")
        flash("Tareas finalizadas", "success")
        return redirect(url_for("home"))
    else:
        flash("Tarea finalizada", "success")

    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    form = FormAltaTarea()
    return render_template(
        "collection/administrar_tareas.html", coleccion=Coleccion.get_by_id(id_coleccion), tareas=tareas, form=form
    )

