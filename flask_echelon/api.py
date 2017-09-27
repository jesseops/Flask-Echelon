import logging

from flask import Blueprint, current_app, jsonify, request, abort
from werkzeug.local import LocalProxy

from flask_echelon import __version__
from .flask_echelon import MemberTypes

manager = LocalProxy(lambda: current_app.echelon_manager)

logger = logging.getLogger(__name__)
EchelonApi = Blueprint('EchelonApi', __name__, url_prefix='/echelonapi')
api = EchelonApi


@api.route('/')
def index():
    return f'{EchelonApi.name} v{__version__}'


@api.route('/echelons')
def echelons():
    return jsonify(list(manager.all_echelons.values()))


@api.route('/echelons/<echelon>')
def get_echelon(echelon):
    e = manager.get_echelon(echelon)
    if e:
        return jsonify(e)
    return f'{echelon} does not exist', 404


@api.route('/echelons/<echelon>', methods=['PUT'])
def create_echelon(echelon):
    if manager.get_echelon(echelon):
        abort(409, f'Tried to create {echelon} but it already exists!')
    e = request.get_json()
    if e.get('echelon', echelon) != echelon:
        abort(400, f'Tried to create {echelon} but was provided inconsistent echelon in request: {e.get("echelon")}')
    manager.define_echelon(echelon, name=e.get('name'), help=e.get('help'))
    for member_type in MemberTypes:
        if member_type.value in e:
            manager.add_member(echelon, e[member_type.value], member_type=member_type)
    return f'{echelon} created', 201


@api.route('/echelons/<echelon>', methods=['POST'])
def edit_echelon(echelon):
    req = request.get_json()
    current_echelon = manager.get_echelon(echelon)
    if not current_echelon:
        abort(404, f'{echelon} does not exist, have you created it?')
    if 'name' in req or 'help' in req:
        manager.define_echelon(echelon,
                               name=req.get('name', current_echelon['name']),
                               help=req.get('help', current_echelon['help']))

    for member_type in MemberTypes:
        if member_type.value in req.get('add', {}):
            manager.add_member(echelon, req['add'][member_type.value], member_type)
        if member_type.value in req.get('remove', {}):
            manager.remove_member(echelon, req['remove'][member_type.value], member_type)
    return f'{echelon} updated', 200


@api.route('/echelons/<echelon>', methods=['DELETE'])
def delete_echelon(echelon):
    manager.remove_echelon(echelon)
    return f'Deleted {echelon} successfully', 200
