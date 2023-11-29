from flask import redirect, render_template, url_for, flash, session, request, Blueprint
from flask_login import login_required
from app.commons.bonita_utils import getActiveCases, getClosedCases
from app.models.collection import Coleccion

bp = Blueprint('metrics', __name__)

@bp.route('/metrics', methods=['POST','GET'])
@login_required
def index():
    """Lista de metricas"""
    # que rol debería ser?
    # if session["current_rol"] == "Creativa":
    casosActivos = len(getActiveCases())
    casosCerrados = len(getClosedCases())
    cantidadDeColeccionesCreadas = len(Coleccion.get_all_colections())
    modeloMasUsado = Coleccion.get_most_used_model()
    cantModeloMasUsado = Coleccion.get_cant_most_used_model()
    return render_template(
        "metrics/index.html",
        casosActivos=casosActivos,
        casosCerrados=casosCerrados,
        cantidadDeColeccionesCreadas=cantidadDeColeccionesCreadas,
        modeloMasUsado=modeloMasUsado,
        cantModeloMasUsado=cantModeloMasUsado,
    )