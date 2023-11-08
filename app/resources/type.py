from flask import Blueprint, redirect, render_template, url_for, flash, session
from flask_login import login_required
from app.form.tipo.alta_tipo import FormAltaTipo
from app.models.tipo import Tipo

bp = Blueprint('type', __name__, url_prefix="/type")

@bp.route('/create', methods=['POST','GET'])
@login_required
def crear():
    """Creación de un nuevo tipo de mueble"""
    #TENDRIA QUE SER CREATIVA
    if session["current_rol"] == "Operaciones":
        form = FormAltaTipo()
        if form.validate_on_submit():
            nombre = form.nombre.data
            Tipo.crear(nombre)
            flash("¡El tipo de mueble fue creado con exito!")
            return redirect(url_for("home"))
        return render_template("type/nuevo.html", form=form)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))