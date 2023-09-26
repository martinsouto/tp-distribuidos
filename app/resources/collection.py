from flask import Blueprint, flash, g, render_template, url_for, request, session, redirect

bp = Blueprint('collection', __name__, url_prefix="/collection")

@bp.route('/create', methods=['POST','GET'])
def create():
    
    return render_template('collection/create.html')