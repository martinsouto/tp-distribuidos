import functools
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.resources.bonita import getUserMembership, loginBonita, logoutBonita
from flask_login import current_user
from flask_login import login_user, logout_user, login_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST','GET'])
def register():
    """Registra un usuario en la base de datos"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'El nombre de usuario es requerido'
        elif not password:
            error = 'La contraseña es requerida'
        elif User.find_by_username(username) is not None:
            error = "El usuario {} ya existe".format(username)
        else:
            session.clear()
            response = loginBonita(username, password)
            if response.status_code != 204:
                error = "El usuario {} no existe en la organización".format(username)
            else:
                user = User(username=username, password=generate_password_hash(password))
                User.create(user)
                return redirect(url_for('auth.login'))
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['POST','GET'])
def login():
  """Logea un usuario en la aplicación"""
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    #remember = True if request.form.get("remember") else False
    user: User = User.find_by_username(username)
    print("Usuario logeado: ",user)
    if not user:
        flash("El usuario y/o la contraseña son incorrectos.")
        return render_template('auth/login.html')

    # chequeamos si el usuario existe en la organización de bonita
    response = loginBonita(user.username, password)
    if response.status_code != 204:
        flash("El usuario no forma parte de la organización.")
        return render_template('auth/login.html')
    login_user(user)
    session["current_rol"] = getUserMembership()
    return redirect(url_for('home'))
  return render_template('auth/login.html')

@login_required
@bp.route('/logout', methods=['POST','GET'])
def logout():
    """Deslogea un usuario de la aplicación"""
    logoutBonita()
    logout_user()
    return redirect('login')