import functools
from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.resources.bonita import loginBonita

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif User.find_by_username(username) is not None:
            error = "User {} already exists, try a different username".format(username)
        else:
            user = User(username=username, password=generate_password_hash(password))
            User.create(user)
            return redirect(url_for('auth.login')) 
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        else:
            user: User = User.find_by_username(username)
            if (user is None) or (not check_password_hash(pwhash=user.password, password=password)):
                error = "Incorrect username and/or password"
            else:
                session.clear()
                loginBonita(username, password)
                session['user_id'] = user.id
                return redirect(url_for('collection.create'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout', methods=['POST','GET'])
def logout():
    session.clear()
    return redirect(url_for('collection.create'))

@bp.before_app_request
def load_logged_in_user():
    if session.get('user_id') is None:
        g.user = None
    else:
        g.user = User.find_by_id(session.get('user_id'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    return wrapped_view