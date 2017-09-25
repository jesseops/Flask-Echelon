import logging

from flask import Blueprint, current_app, jsonify

from flask_echelon import __version__

logger = logging.getLogger(__name__)
EchelonApi = Blueprint('EchelonApi', __name__, url_prefix='/echelonapi')
api = EchelonApi


@api.route('/')
def index():
    return f'{EchelonApi.name} v{__version__}'


@api.route('/echelons')
def echelons():
    return jsonify(current_app.echelon_manager.all_echelons)


@api.route('/echelons/<echelon>')
def echelon(echelon):
    return jsonify(current_app.echelon_manager.get_echelon(echelon))
