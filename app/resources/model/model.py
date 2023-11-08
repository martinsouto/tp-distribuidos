from flask import Blueprint, redirect, render_template, url_for, flash, session, request
from flask_login import login_required
from app.form.modelo.alta_modelo import FormAltaModelo
from app.models.model import Modelo
from app.models.tipo import Tipo

bp = Blueprint('model', __name__, url_prefix="/model")

@bp.route('/create', methods=['POST','GET'])
@login_required
def crear():
    """Creación de un nuevo modelo"""
    #TENDRIA QUE SER CREATIVA
    if session["current_rol"] == "Operaciones":
        form = FormAltaModelo()
        if form.validate_on_submit():
            nombre = form.nombre.data
            descripcion = form.descripcion.data
            tipo = request.form.get("tipo")
            Modelo.crear(nombre, descripcion, tipo)
            flash("¡El modelo fue creado con exito!")
            return redirect(url_for("home"))
        tipos = Tipo.tipos()
        return render_template("model/create.html", form=form, tipos=tipos)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))