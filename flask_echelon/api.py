import logging

from flask import Blueprint

# from flask_echelon import __version__

logger = logging.getLogger(__name__)
EchelonApi = Blueprint('EchelonApi', __name__, url_prefix='/echelon')


@EchelonApi.route('/')
def index():
    return 'Echelon Api'
