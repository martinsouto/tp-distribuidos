import time
from flask import Blueprint, redirect, render_template, url_for, flash, session, request
from flask_login import login_required, current_user
import requests
import json
from app.form.coleccion.eleccion_materiales import FormEleccionMateriales
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
        form = FormEleccionMateriales()
        """Template Seleccionar materiales"""
        materiales = Material.materiales()
        return render_template(
            "collection/seleccion_materiales.html",
            materiales=materiales,
            id_coleccion=id_coleccion,
            form=form,
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
        form = FormEleccionMateriales()
        if form.validate_on_submit():
            """Template Seleccionar materiales"""
            materiales = request.form.getlist("materiales[]")
            #obtengo la fecha de entrega seleccionada
            fecha_entrega = request.form.get("fecha_entrega")
            print("LA FECHA DE ENTREGA SELECCIONADA ES: ", fecha_entrega)
            token = login_api_materiales()
            listado = listado_api_materiales(token, materiales)
            # filtramos materiales obtenidos
            mats_obtenidos = [material["name"] for material in listado]
            # filtramos stocks para utilizarlos mas adelante
            stocks = [material["stock"] for material in listado]
            # filtramos delivery_time para utilizarlos mas adelante
            delivery_time = [material["delivery_time"] for material in listado]
            print("DELIVERY TIMEEEEEE", delivery_time)
            print("MATERIALES OBTENIDOS", mats_obtenidos)
            #Asigno y finalizo tarea de definición de materiales
            taskId = getUserTaskByName(
                "Definir Materiales necesarios", Coleccion.get_by_id(id_coleccion).case_id
            )
            assign_task(taskId)
            updateUserTask(taskId, "completed")
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
                fecha_entrega=fecha_entrega,
                delivery_time=delivery_time,
            )
        else:
            print("IMPRIMO ERROR DE FORMULARIO")
            print(form.errors)
            return render_template(
                    "collection/seleccion_materiales.html",
                    form=form,
                    materiales=materiales_todos,
                    id_coleccion=id_coleccion,
                )

    flash("Algo falló", "error")
    return render_template(
        "collection/seleccion_materiales.html", materiales=materiales_todos
    )


@login_required
def login_api_materiales():
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/login"
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
    URL = "http://127.0.0.1:7000/materiales"
    body = {"names": materiales}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_materiales(token, id_coleccion):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/reservar_materiales"
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
        delivery_time= eval(
            request.form.getlist("delivery_time[]")[0]
        ) # uso eval para volverlo dict
        #recibo la fecha de entrega
        fecha_entrega = request.form.get("fecha_entrega")
        #paso de cadena a datetime
        fecha_entrega_as_datetime = datetime.strptime(fecha_entrega, '%Y-%m-%d')
        #guardo la fecha de entrega de materiales en la coleccion
        Coleccion.get_by_id(id_coleccion).modificar_entrega_materiales(fecha_entrega_as_datetime)
        print("delivery time", delivery_time)
        print(stocks)
        #print(delivery_time)
        listado = []
        for i in range(len(materiales)):
            if cantidades[i] != "0":
                if int(cantidades[i]) > stocks[i]:
                    flash("Stock insuficiente, reprogramar", "error")
                #chequear que delivery time sea menor a la fecha de entrega menos la fecha actual
                elif int(delivery_time[i]) > (fecha_entrega_as_datetime - datetime.now()).days:
                    flash("Tiempo de entrega insuficiente, reprogramar", "error")
                else:
                    listado.append(
                        {"id": materiales[i]["id"], "quantity": int(cantidades[i])}
                    )
                    print(json.dumps(listado))
                    Coleccion.get_by_id(id_coleccion).save_materials(str(json.dumps(listado)))
                    set_bonita_variable(
                        Coleccion.get_by_id(id_coleccion).case_id,
                        "hay_materiales",
                        "true",
                        "java.lang.Boolean",
                    )
                    flash("Materiales guardados!", "success")
                    while "Consulta de Disponibilidad de Materiales" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id):
                        print("Cargando...")
                    #Asgino y finalizo Consulta de materiales
                    taskIdConsultaMateriales = getUserTaskByName(
                        "Consulta de Disponibilidad de Materiales", Coleccion.get_by_id(id_coleccion).case_id
                    )
                    assign_task(taskIdConsultaMateriales)
                    updateUserTask(taskIdConsultaMateriales, "completed")
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
    while ("Elaborar plan de fabricacion" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
        print("Cargando...")
    return redirect(url_for("home"))

# ESPACIOS
@bp.route('/<int:id_coleccion>/reservar_espacio', methods=['POST'])
@login_required
def reservar_espacio(id_coleccion):
    """Se reserva un espacio"""
    case_id = Coleccion.get_by_id(id_coleccion).case_id
    if session["current_rol"] == "Operaciones":
        #obtengo la variable de bonita materiales_reservados
        materiales_reservados=get_bonita_variable(Coleccion.get_by_id(id_coleccion).case_id, "materiales_reservados")
        if materiales_reservados != "true":
            # Seteo la variable de bonita materiales_atrasados
            set_bonita_variable(
                    case_id, "materiales_atrasados", "false", "java.lang.Boolean"
                )
            while ("Consulta de espacio de fabricacion" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
                print("Cargando...")
            taskId = getUserTaskByName(
                "Consulta de espacio de fabricacion",
                case_id,
            )
            # Seteo la variable de bonita sedes_disponibles
            set_bonita_variable(
                case_id, "sedes_disponibles", "true", "java.lang.Boolean"
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")

            # Reservo los materiales guardados (si es que no los tengo, eso lo chequea bonita automaticamente con la variable "materiales_disponibles")
            while ("Reserva de materiales necesarios" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
                print("Cargando...")
            taskId = getUserTaskByName(
                "Reserva de materiales necesarios",
                case_id,
            )
            assign_task(taskId)
            token = login_api_materiales()
            reservar_api_materiales(token, id_coleccion)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")

            #seteo la variable de bonita materiales_reservados
            set_bonita_variable(
                case_id, "materiales_reservados", "true", "java.lang.Boolean"
            )

        #si ya tengo los materiales reservados, completo la consulta del espacio de fabricacion
        if materiales_reservados == "true":
            while ("Consulta de espacio de fabricacion" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
                print("Cargando...")
            taskId = getUserTaskByName(
                "Consulta de espacio de fabricacion",
                case_id,
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            #seteo espacios_disponibles en true
            set_bonita_variable(
                case_id, "sedes_disponibles", "true", "java.lang.Boolean"
            )
        while ("Reserva de espacio de fabricacion" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
            print("Cargando...")
        taskId = getUserTaskByName(
            "Reserva de espacio de fabricacion",
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
        
        flash("Reservas realizadas!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def login_api_espacios():
    requestSession = requests.Session()
    URL = "http://127.0.0.1:6000/login"
    #body = {"username": current_user.username, "password": current_user.password}
    #hardcodeo con el usuario y contraseña que tengo en la base de datos de la api
    body = {"username": "martin", "password": "1234"}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    print(response)
    token = response.json()["token"]
    return token


@login_required
def listado_api_espacios(token, end_date):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:6000/espacios"
    body = {"end_date": end_date}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_espacios(token, space_id, id_coleccion):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:6000/reservar_espacio"
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

@bp.route('/<int:id_coleccion>/seleccionar_espacio', methods=['GET', 'POST'])
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
                "collection/seleccion_espacio.html",
                espacios=espacios,
                id_coleccion=id_coleccion,
                fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
                fecha_recepcion_materiales=Coleccion.get_by_id(id_coleccion).fecha_recepcion_materiales,
            )
        else:
            flash("No hay espacios disponibles, (REPROGRAMAR)", "error")
            return redirect(url_for("home"))
    flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@login_required
@bp.route('/<int:id_coleccion>/recibir_materiales', methods=['GET', 'POST'])
def recibir_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        #chequeo si la fecha actual es mayor a la fecha de recepcion de materiales
        if datetime.now() > Coleccion.get_by_id(id_coleccion).fecha_recepcion_materiales:
            # Seteo la variable de bonita materiales_atrasados
            set_bonita_variable(
                Coleccion.get_by_id(id_coleccion).case_id, "materiales_atrasados", "true", "java.lang.Boolean"
            )
            set_bonita_variable(
                Coleccion.get_by_id(id_coleccion).case_id, "materiales_disponibles", "true", "java.lang.Boolean"
            )
            flash("Materiales recibidos atrasados, (REPROGRAMAR)", "error")
        else:
            # Seteo la variable de bonita materiales_atrasados en false
            set_bonita_variable(
                Coleccion.get_by_id(id_coleccion).case_id, "materiales_atrasados", "false", "java.lang.Boolean"
            )
            set_bonita_variable(
                Coleccion.get_by_id(id_coleccion).case_id, "materiales_disponibles", "true", "java.lang.Boolean"
            )
            flash("Materiales recibidos!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    while ("Esperar materiales" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
        print("Cargando...")
    taskId = getUserTaskByName(
        "Esperar materiales",
        Coleccion.get_by_id(id_coleccion).case_id,
    )
    assign_task(taskId)
    # Se finaliza la tarea
    updateUserTask(taskId, "completed")
    # Espero a que avance a la siguiente tarea antes de redirigir al home, para mostrar bien los botones
    while ("Elaborar plan de fabricacion" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id) and "Seleccionar fecha de lanzamiento" not in get_ready_tasks(Coleccion.get_by_id(id_coleccion).case_id)):
        print("Cargando...")
    return redirect(url_for("home"))
