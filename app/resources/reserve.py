import time
from flask import Blueprint, redirect, render_template, url_for, flash, session, request
from flask_login import login_required, current_user
import requests
import json
from app.models.collection import Coleccion
from app.models.material import Material
from datetime import datetime
from app.resources.bonita import *
from app.resources.collection import bp

# MATERIALES
@bp.route('/<int:id_coleccion>/seleccionar_materiales', methods=['GET', 'POST'])
@login_required
def seleccionar_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        """Template Seleccionar materiales"""
        materiales = Material.materiales()
        return render_template(
            "collection/seleccion_materiales.html",
            materiales=materiales,
            id_coleccion=id_coleccion,
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@bp.route('/<int:id_coleccion>/seleccion_materiales', methods=['POST'])
@login_required
def seleccion_materiales(id_coleccion):
    print("ENTREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE PTM")
    materiales_todos = Material.materiales()
    if session["current_rol"] == "Operaciones":
        """Template Seleccionar materiales"""
        materiales = request.form.getlist("materiales[]")
        token = login_api_materiales()
        listado = listado_api_materiales(token, materiales)
        # filtramos materiales obtenidos
        mats_obtenidos = [material["name"] for material in listado]
        # filtramos stocks para utilizarlos mas adelante
        stocks = [material["stock"] for material in listado]
        if not (set(materiales) == set(mats_obtenidos)):
            materiales_faltan = [i for i in materiales if i not in mats_obtenidos]
            flash(
                "Faltan los siguientes materiales: " + str(materiales_faltan), "error"
            )
            return render_template(
                "collection/seleccion_materiales.html",
                materiales=materiales_todos,
                id_coleccion=id_coleccion,
            )
        return render_template(
            "collection/guardar_materiales.html",
            materiales=listado,
            stocks=stocks,
            id_coleccion=id_coleccion,
            fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
        )
    flash("Algo falló", "error")
    return render_template(
        "collection/seleccion_materiales.html", materiales=materiales_todos
    )


@login_required
def login_api_materiales():
    requestSession = requests.Session()
    URL = "https://apidssd.onrender.com/login"
    #body = {"username": current_user.username, "password": "bpm"}
    #hardcodeo con el usuario y contraseña que tengo en la base de datos de render
    body = {"username": "martin", "password": "1234"}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    print("IMPRIMO EL TOKEN DEL LOGIN MATERIALES API")
    print(response)
    token = response.json()["token"]
    return token


@login_required
def listado_api_materiales(token, materiales):
    requestSession = requests.Session()
    URL = "https://apidssd.onrender.com/materiales"
    body = {"names": materiales}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_materiales(token, id_coleccion):
    requestSession = requests.Session()
    URL = "https://apidssd.onrender.com/reservar_materiales"
    body = {
        "materials": eval(Coleccion.get_by_id(id_coleccion).materiales), #convierto el str a dict
        "user_id": int(get_user_id()),
        "colection_id": int(id_coleccion),
    }
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    print(data)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    print(response)
    print(listado)
    return listado

@bp.route('/<int:id_coleccion>/guardar_materiales', methods=['POST'])
@login_required
def guardar_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        """Template Reservar materiales"""
        token = login_api_materiales()
        materiales = eval(
            request.form.getlist("materiales[]")[0]
        )  # uso eval para volverlo dict
        stocks = eval(
            request.form.getlist("stocks[]")[0]
        )  # uso eval para volverlo dict
        cantidades = request.form.getlist("cantidad[]")
        print(stocks)
        listado = []
        for i in range(len(materiales)):
            if cantidades[i] != "0":
                if int(cantidades[i]) > stocks[i]:
                    flash("Stock insuficiente", "error")
                    return render_template(
                        "collection/guardar_materiales.html",
                        materiales=materiales,
                        stocks=stocks,
                        id_coleccion=id_coleccion,
                        fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
                    )
                else:
                    listado.append(
                        {"id": materiales[i]["id"], "quantity": int(cantidades[i])}
                    )
        print(json.dumps(listado))
        Coleccion.get_by_id(id_coleccion).save_materials(str(json.dumps(listado)))
        set_bonita_variable(
            Coleccion.get_by_id(id_coleccion).case_id,
            "materiales_disponibles",
            "true",
            "java.lang.Boolean",
        )
        #Asigno y finalizo tarea de definición de materiales
        taskId = getUserTaskByName(
            "Definir Materiales necesarios", Coleccion.get_by_id(id_coleccion).case_id
        )
        assign_task(taskId)
        updateUserTask(taskId, "completed")
        while "Consulta de Disponibilidad de Materiales" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id):
                print("Cargando...")
        #Asgino y finalizo Consulta de materiales
        taskIdConsultaMateriales = getUserTaskByName(
            "Consulta de Disponibilidad de Materiales", Coleccion.get_by_id(id_coleccion).case_id
        )
        assign_task(taskIdConsultaMateriales)
        updateUserTask(taskIdConsultaMateriales, "completed")
        flash("Materiales guardados!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@login_required
def recibir_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        # Seteo la variable de bonita materiales_disponibles
        set_bonita_variable(
            Coleccion.get_by_id(id_coleccion).case_id, "materiales_disponibles", "true", "java.lang.Boolean"
        )
        flash("Materiales recibidos!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    # Espero a que avance a la siguiente tarea antes de redirigir al home, para mostrar bien los botones
    while ("Elaborar plan de fabricación" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
        print("Cargando...")
    return redirect(url_for("home"))

# ESPACIOS
@login_required
def reservar_espacio(id_coleccion):
    """Se reserva un espacio"""
    if session["current_rol"] == "Operaciones":
        case_id = Coleccion.get_by_id(id_coleccion).case_id
        # Seteo la variable de bonita materiales_atrasados
        set_bonita_variable(
                case_id, "materiales_atrasados", "false", "java.lang.Boolean"
            )
        while ("Consultar espacio de fabricación" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
            print("Cargando...")
        taskId = getUserTaskByName(
            "Consultar espacio de fabricación",
            case_id,
        )
        # Seteo la variable de bonita plazos_fabricacion
        set_bonita_variable(
            case_id, "plazos_fabricacion", "true", "java.lang.Boolean"
        )
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")

        # Reservo los materiales guardados (si es que no los tengo, eso lo chequea bonita automaticamente con la variable "materiales_disponibles")
        while ("Reservar materiales" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
            print("Cargando...")
        taskId = getUserTaskByName(
            "Reservar materiales",
            case_id,
        )
        assign_task(taskId)
        token = login_api_materiales()
        reservar_api_materiales(token, id_coleccion)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")

        while ("Reservar espacio de fabricación" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
            print("Cargando...")
        taskId = getUserTaskByName(
            "Reservar espacio de fabricación",
            case_id,
        )
        assign_task(taskId)
        token = login_api_espacios()
        space_id = int(request.form.get("espacio"))
        espacio = reservar_api_espacios(token, space_id, id_coleccion)
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(espacio["start_date"])
        print(espacio["end_date"])
        Coleccion.get_by_id(id_coleccion).save_espacio_fabricacion(espacio["start_date"], espacio["end_date"])
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
        
        #Borro los materiales guardados de la colección
        Coleccion.get_by_id(id_coleccion).delete_materials()
        
        flash("Materiales y espacio de fabricación reservados!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def login_api_espacios():
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/login"
    body = {"username": current_user.username, "password": current_user.password}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    print(response)
    token = response.json()["token"]
    return token


@login_required
def listado_api_espacios(token, end_date):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/espacios"
    body = {"end_date": end_date}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_espacios(token, space_id, id_coleccion):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/reservar_espacio"
    body = {
        "space_id": space_id,
        "user_id": int(get_user_id()),
        "colection_id": int(id_coleccion),
    }
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    print(data)
    response = requestSession.put(URL, data=data, headers=headers)
    espacio = response.json()
    print(response)
    print(espacio)
    return espacio


@login_required
def seleccionar_espacio(id_coleccion):
    """Template para seleccionar espacio espacio"""
    # cambiar a operaciones
    if session["current_rol"] == "Operaciones":
        token = login_api_espacios()
        end_date = str((Coleccion.get_by_id(id_coleccion).fecha_entrega).date())
        espacios = listado_api_espacios(token, end_date)
        case_id = Coleccion.get_by_id(id_coleccion).case_id
        if espacios:
            return render_template(
                "coleccion/seleccion_espacio.html",
                espacios=espacios,
                id_coleccion=id_coleccion,
                fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
                fecha_actual=datetime.now()
            )
        else:
            flash("No hay espacios disponibles", "error")
            return redirect(url_for("home"))
    flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))
