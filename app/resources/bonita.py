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
    print("Response del login:")
    print(response)
    # si todo sale bien seteo las variables de sesión
    if response.status_code == 204:
        session["JSESSION"] = "JSESSIONID=" + response.cookies.get("JSESSIONID")
        session["bonita_token"] = response.cookies.get("X-Bonita-API-Token")
        print("Bonita-Api-Token: " + response.cookies.get("X-Bonita-API-Token"))
        print("JSESSIONID: " + response.cookies.get("JSESSIONID"))
    # devuelvo la respuesta para saber si puedo loguearme o no
    return response

def logoutBonita():
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/logoutservice"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.get(URL, headers=headers)
    print("Response de logout Bonita:")
    print(response)

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
    #print(response.json()["value"])

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
    taskId = response.json()[0]["id"]
    return taskId

def get_user_id():
    """Se recupera el id del usuario logeado"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/system/session/unusedId"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get user id:")
    print(response)
    print(response.json()["user_id"])
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

def getUserMembership():
    print("ENTRE A GET USER MEMBER SHIP")
    requestSession = requests.Session()
    user = getLoggedUser()
    params = {"f": "user_id=" + user["id"], "d": "role_id"}
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    URL = "http://localhost:8080/bonita/API/identity/membership"
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response de getUserMemebership:")
    print(response)
    print("rol:")
    print(response.json()[0]["role_id"]["name"])
    return response.json()[0]["role_id"]["name"]

def getLoggedUser():
    requestSession = requests.Session()
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    URL = "http://localhost:8080/bonita/API/system/session/unusedid"
    response = requestSession.get(URL, headers=headers)
    print("Response de getLoggedUser:")
    print(response)
    print("username: " + response.json()["user_name"])
    return {
        "id": response.json()["user_id"],
        "username": response.json()["user_name"],
    }

def get_ready_tasks(case_id):
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/humanTask/"
    )
    headers = getBonitaHeaders()
    params = {"f": "caseId="+str(case_id)}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response del get tareas ready para el case "+str(case_id)+":")
    tareas = []
    print(response.status_code)
    if response.status_code == 200:
        tareas = [task["name"] for task in response.json()]
    print(tareas)
    return tareas

def get_completed_tasks_by_name(case_id, name):
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/archivedHumanTask?f=caseId="+str(case_id)+"&f=name="+name
    )
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get tareas completed para el case "+str(case_id)+":")
    tareas = []
    print(response.status_code)
    if response.status_code == 200:
        tareas = [task["name"] for task in response.json()]
    print(tareas)
    return tareas