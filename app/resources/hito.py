import time
from flask import (
    redirect, render_template, url_for, flash, session, request, Blueprint
)
from flask_login import login_required, current_user
from app.models.hito import Hito
from app.models.collection import Coleccion
from app.form.hito.alta_hito import FormAltaHito
from datetime import datetime
from app.resources.bonita import assign_task, get_ready_tasks, getUserTaskByName, set_bonita_variable, updateUserTask
from app.resources.collection import bp
#REFACTORIZADO
@bp.route('/<int:id_coleccion>/crear_hito', methods=['POST'])
@login_required
def crear_hito(id_coleccion):
    coleccion = Coleccion.get_by_id(id_coleccion)
    if session["current_rol"] != "Operaciones":
        flash("No tienes permiso para acceder a este sitio", "error")
        return redirect(url_for("home"))

    form = FormAltaHito()
    form.fin_fabricacion = coleccion.fin_fabricacion
    form.id_coleccion = id_coleccion

    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        fecha_limite = form.fecha_limite.data
        Hito.crear(nombre, descripcion, fecha_limite, id_coleccion)
        flash("Hito creado", "success")
    else:
        flash("Hay errores en los campos del hito", "error")

    hitos = Hito.get_by_coleccion_id(id_coleccion)
    return render_template(
        "collection/planificar_fabricacion.html", coleccion=coleccion, hitos=hitos, form=form
    )

@bp.route('/<int:id_coleccion>/<int:id_hito>/eliminar', methods=['GET', 'DELETE'])
@login_required
def eliminar_hito(id_coleccion, id_hito):
    if session["current_rol"] != "Operaciones":
        flash("No tienes permiso para acceder a este sitio", "error")
        return redirect(url_for("home"))

    hito = Hito.get_by_id(id_hito)
    hito.eliminar()
    flash("Hito eliminado", "success")

    hitos = Hito.get_by_coleccion_id(id_coleccion)
    form = FormAltaHito()
    return render_template(
        "collection/planificar_fabricacion.html", coleccion=Coleccion.get_by_id(id_coleccion), hitos=hitos, form=form
    )

@bp.route('/<int:id_coleccion>/<int:id_hito>/finalizar', methods=['GET','POST'])
@login_required
def finalizar_hito(id_coleccion, id_hito):
    if session["current_rol"] != "Operaciones":
        flash("No tienes permiso para acceder a este sitio", "error")
        return redirect(url_for("home"))

    hito = Hito.get_by_id(id_hito)
    hito.finalizar()

    if Hito.coleccion_finalizada(id_coleccion):
        coleccion = Coleccion.get_by_id(id_coleccion)
        #obtengo el usuario que creo la coleccion
        user = Coleccion.get_by_id(id_coleccion).get_creador()
        #armo el email haciendo user.username + @gmail.com
        email = user.username + "@gmail.com"
        #imprimo el email para ver si esta bien
        print(email)
        set_bonita_variable(coleccion.case_id, "userEmail", email, "java.lang.String")
        flash("Hitos finalizados", "success")
        set_bonita_variable(coleccion.case_id, "hitos_cumplidos", "true", "java.lang.Boolean")
        set_bonita_variable(coleccion.case_id, "coleccion_finalizada", "true", "java.lang.Boolean")
        set_bonita_variable(coleccion.case_id, "reprogramar_lanzamiento", "false", "java.lang.Boolean")
        while ("Esperar finalizar hitos" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
            print("Cargando...")
        taskId = getUserTaskByName(
            "Esperar finalizar hitos",
            Coleccion.get_by_id(id_coleccion).case_id,
        )
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
    else:
        flash("Hito finalizado", "success")
    hitos = Hito.get_by_coleccion_id(id_coleccion)
    form = FormAltaHito()
    return render_template(
        "collection/administrar_hitos.html", coleccion=Coleccion.get_by_id(id_coleccion), hitos=hitos, form=form
    )

