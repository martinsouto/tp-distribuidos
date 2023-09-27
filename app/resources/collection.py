from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.resources.auth import portal_login
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
import json  # Importa la biblioteca json
import requests  # Importa la biblioteca requests

bp = Blueprint('collection', __name__, url_prefix="/collection")

@bp.route('/create', methods=['POST','GET'])
def create():
    """Creación de una nueva coleccion"""
    print("ENTRO AL METODO CREATE")
    form = FormAltaColeccion()
    if form.validate_on_submit():
        print("ENVIO FORMULARIO")
        response = portal_login();
        print("SALI DE PORTAL_LOGIN")
        nombre = form.nombre.data
        print(nombre)
        #fecha_lanzamiento = form.fecha_lanzamiento.data
        #modelos = request.form.getlist("modelos[]")
        #Coleccion.crear(nombre, fecha_lanzamiento, current_user.id, modelos)
        # Se instancia la tarea
        print("entro a init process ")
        case_id = init_process()
        print("salgo de init process")
        # Se le asigna la tarea al usuario que creó la colección
        # assign_task()
        # Se finaliza la tarea
        # to-do
        # Cargar la variable en bonita
        #coleccion_id = Coleccion.get_by_name(nombre).id
        #acá hardcodeo el id de la colección xq todavía ni tenemos los modelos
        print("entro a set_bonita_variable")
        set_bonita_variable(case_id, "coleccion_id", 1, "java.lang.Integer")
        print("salgo de set_bonita_variable")
        flash("¡La colección fue creada con exito!")
        return render_template('collection/create.html', form=form)
        #return redirect(url_for("home"))
    # Si el formulario no se ha enviado o hay errores de validación,
    # simplemente muestra el formulario nuevamente
    print("Entro al formulario")
    return render_template('collection/create.html', form=form)

def init_process():
    # se le pega a la API y se recupera el id del proceso
    print("ENTRE A INIT_PROCESS")
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    processId = response.json()[0]["id"]

    print("Response del get id del proceso:")
    print(response)
    print("Process ID: " + response.json()[0]["id"])

    # se instancia el proceso con su id, creando una tarea
    URL = "http://localhost:8080/bonita/API/bpm/process/" + processId + "/instantiation"
    headers = getBonitaHeaders()
    response = requestSession.post(URL, headers=headers)

    print("Response al instanciar proceso:")
    print(response)
    case_id = response.json()["caseId"]
    print("Case ID:")
    print(case_id)
    return case_id

def set_bonita_variable(case_id, variable_name, variable_value, type):
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/caseVariable/"
        + str(case_id)
        + "/"
        + variable_name
    )
    body = {"value": variable_value, "type": type}
    headers = getBonitaHeaders()
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print("Response de setear variable bonita:")
    print(response)
    response = requestSession.get(URL, headers=headers)
    print("Response al hacer get de variable bonita:")
    print(response)
    print("Valor de la variable coleccion_id:")
    print(response.json()["value"])

def getBonitaHeaders():
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    return headers

