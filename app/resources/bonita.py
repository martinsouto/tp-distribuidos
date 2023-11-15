from flask import session
import json  # Importa la biblioteca json
import requests  # Importa la biblioteca requests

def loginBonita(username, password):
    """Se logea y obtiene la cookie de bonita"""
    URL = "http://localhost:8080/bonita/loginservice"
    body = {"username": username, "password": password, "redirect": "false"}
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    requestSession = requests.Session()
    response = requestSession.post(URL, data=body, headers=headers)
    print("Response del login:", response)
    # si todo sale bien seteo las variables de sesión
    if response.status_code == 204:
        session["JSESSION"] = "JSESSIONID=" + response.cookies.get("JSESSIONID")
        session["bonita_token"] = response.cookies.get("X-Bonita-API-Token")
        print("Bonita-Api-Token: " + response.cookies.get("X-Bonita-API-Token"))
        print("JSESSIONID: " + response.cookies.get("JSESSIONID"))
    # devuelvo la respuesta para saber si puedo loguearme o no
    return response

def logoutBonita():
    """Se deslogea de bonita"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/logoutservice"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response de logout Bonita:", response)

def init_process():
    """Se inicia el proceso de bonita"""
    # Se recupera el ID del proceso
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    processId = response.json()[0]["id"]
    # Se instancia el proceso con su id, creando una tarea
    URL = "http://localhost:8080/bonita/API/bpm/process/" + processId + "/instantiation"
    response = requestSession.post(URL, headers=headers)
    case_id = response.json()["caseId"]
    print("Case ID:", case_id)
    return case_id

def set_bonita_variable(case_id, variable_name, variable_value, type):
    """Se setea una variable en el proceso"""
    requestSession = requests.Session()
    URL = ("http://localhost:8080/bonita/API/bpm/caseVariable/"+ str(case_id)+ "/"+ variable_name)
    body = {"value": variable_value, "type": type}
    headers = getBonitaHeaders()
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)

def getBonitaHeaders():
    """Se obtienen las cookies de bonita"""
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
    taskId = response.json()[0]["id"]
    return taskId

def get_user_id():
    """Se recupera el id del usuario logeado"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/system/session/unusedId"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    user_id = response.json()["user_id"]
    return user_id


def assign_task(taskId):
    """Se le asigna una tarea al usuario logeado"""
    requestSession = requests.Session()
    user_id = get_user_id()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"assigned_id": user_id}
    # Lo convierto a json porque sino tira 500
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)

def updateUserTask(taskId, state):
    """Se actualiza el estado de la tarea de usuario"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"state": state}
    # Lo convierto a json porque sino tira 500
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)

def getUserMembership():
    """Se obtiene el rol del usuario logeado"""
    requestSession = requests.Session()
    user = getLoggedUser()
    params = {"f": "user_id=" + user["id"], "d": "role_id"}
    headers = getBonitaHeaders()
    URL = "http://localhost:8080/bonita/API/identity/membership"
    response = requestSession.get(URL, headers=headers, params=params)
    return response.json()[0]["role_id"]["name"]

def getLoggedUser():
    """Se obtiene el usuario logeado"""
    requestSession = requests.Session()
    headers = getBonitaHeaders()
    URL = "http://localhost:8080/bonita/API/system/session/unusedid"
    response = requestSession.get(URL, headers=headers)
    return {
        "id": response.json()["user_id"],
        "username": response.json()["user_name"],
    }

def get_ready_tasks(case_id):
    """Se obtienen las tareas listas para ser realizadas"""
    requestSession = requests.Session()
    URL = ("http://localhost:8080/bonita/API/bpm/humanTask/")
    headers = getBonitaHeaders()
    params = {"f": "caseId="+str(case_id)}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response del get tareas ready para el case "+str(case_id)+":")
    tareas = []
    if response.status_code == 200:
        tareas = [task["name"] for task in response.json()]
    print(tareas)
    return tareas

def get_completed_tasks_by_name(case_id, name):
    """Se obtienen las tareas completadas por nombre"""
    requestSession = requests.Session()
    URL = ("http://localhost:8080/bonita/API/bpm/archivedHumanTask?f=caseId="+str(case_id)+"&f=name="+name)
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get tareas completed para el case "+str(case_id)+":")
    tareas = []
    print(response.status_code)
    if response.status_code == 200:
        tareas = [task["name"] for task in response.json()]
    print(tareas)
    return tareas

def deleteCase(case_id):
    """Se elimina el case"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/case/" + str(case_id)
    headers = getBonitaHeaders()
    response = requestSession.delete(URL, headers=headers)

def get_bonita_variable(case_id, variable_name):
    """Se obtiene una variable del proceso"""
    requestSession = requests.Session()
    URL = ("http://localhost:8080/bonita/API/bpm/caseVariable/"+ str(case_id)+ "/"+ variable_name)
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    if response.status_code == 200:
        print("Response del get variable "+variable_name+" para el case "+str(case_id)+":", response.json()["value"])
        return response.json()["value"]
    else:
        return False