from flask import render_template, redirect, session, url_for, request, flash
import requests

def portal_login():
    """Se logea y obtiene la cookie de bonita"""
    URL = "http://localhost:8080/bonita/loginservice"
    body = {"username": "walter.bates", "password": "bpm", "redirect": "false"}
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