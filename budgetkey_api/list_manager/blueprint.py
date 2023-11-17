from dgp_oauth2.lib import Verifyer

from flask import Blueprint, request, abort
from flask_jsonpify import jsonpify

from .controllers import store, get, delete, delete_all
from .models import setup_engine
from .config import db_connection_string

import logging


def list_manager_blueprint(verifyer_args=None, enable_mock_oauth=None): #noqa
    """Create blueprint.
    """
    setup_engine(db_connection_string)

    # Create instance
    blueprint = Blueprint('budgetkey_list_manager', 'budgetkey_list_manager')

    verifyer = Verifyer(**verifyer_args)

    # Controller Proxies
    store_controller = store
    get_controller = get
    delete_controller = delete
    delete_all_controller = delete_all

    def get_permissions():
        token = request.headers.get('auth-token') or request.values.get('jwt')
        permissions = verifyer.extract_permissions(token)
        if not permissions and enable_mock_oauth:
            logging.warning("Failed to verify permissions, continuing with mock permissions")
            permissions = {"userid": str(token)}
        return permissions

    def store_():
        permissions = get_permissions()
        if permissions is False:
            abort(403)
        list_name = request.values.get('list')
        item = request.get_json()
        if None in (list_name, item):
            abort(400)
        return jsonpify(store_controller(permissions, list_name, item))

    def read_():
        permissions = get_permissions()
        if permissions is False:
            abort(403)
        list_name = request.values.get('list')
        if not list_name:
            abort(400)
        return jsonpify(get_controller(permissions, list_name))

    def delete_():
        permissions = get_permissions()
        if permissions is False:
            abort(403)
        list_name = request.values.get('list')
        item_id = request.values.get('item_id')
        if None in (list_name, item_id):
            abort(400)
        if item_id == 'all':
            return jsonpify(delete_all_controller(permissions, list_name))
        else:
            return jsonpify(delete_controller(permissions, item_id))

    # Register routes
    blueprint.add_url_rule(
        '/', 'put', store_, methods=['PUT'])
    blueprint.add_url_rule(
        '/', 'delete', delete_, methods=['DELETE'])
    blueprint.add_url_rule(
        '/', 'get', read_, methods=['GET'])

    # Return blueprint
    return blueprint
