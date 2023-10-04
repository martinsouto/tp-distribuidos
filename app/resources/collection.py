from pipes import quote
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.resources.auth import portal_login
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
import json  # Importa la biblioteca json
import requests  # Importa la biblioteca requests

bp = Blueprint('collection', __name__, url_prefix="/collection")

@bp.route('/create', methods=['POST','GET'])
def create():
    """Creación de una nueva coleccion"""
    form = FormAltaColeccion()
    if form.validate_on_submit():
        response = portal_login();
        nombre = form.nombre.data
        #por ahora no hacemos nada con los datos del formulario por que no tenemos modelos
        # Se instancia la tarea
        case_id = init_process()
        # Obtengo id de tarea
        taskId = getUserTaskByName("Planificar la coleccion", case_id)
        # Se le asigna la tarea al usuario que creó la colección
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

def init_process():
    # Se le pega a la API y se recupera el id del proceso
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    print(URL)
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    processId = response.json()[0]["id"]
    print("Response del init_process:")
    print(response)
    print("Process ID: " + response.json()[0]["id"])
    # Se instancia el proceso con su id, creando una tarea
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

def getUserTaskByName(taskName, caseId):
    """Obtengo la tarea por su case y name para tener su id"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask?f=caseId="+str(caseId)+"&f=name="+taskName
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get user task para el case "+str(caseId)+":")
    print(URL)
    print("Response del getUserTaskByName")
    print(response)
    response = requestSession.get(URL, headers=headers)
    # Verifica si la respuesta tiene contenido y es JSON válido
    if response.status_code == 200:
        try:
            response_json = response.json()
            if response_json:
                # La respuesta es un objeto JSON válido y contiene datos
                print("La respuesta contiene datos:", response_json)
                first_task = response_json[0]
                task_id = first_task.get("id")
                print(task_id)
            else:
                # La respuesta está vacía
                print("La respuesta está vacía")
        except json.JSONDecodeError:
            # No se pudo analizar la respuesta como JSON
            print("La respuesta no es JSON válido")
    else:
        # La solicitud no fue exitosa (código de estado diferente de 200)
        print("La solicitud no fue exitosa (código de estado:", response.status_code, ")")

    return task_id

def assign_task(taskId):
    """Se le asigna una tarea al usuario logeado"""
    requestSession = requests.Session()
    user_id = "1"
    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"assigned_id": user_id}
    # Lo convierto a json porque sino tira 500
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print("responde del assign_task")
    print(response)

def updateUserTask(taskId, state):
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"state": state}
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print("Print del update user task:")
    print(response)

