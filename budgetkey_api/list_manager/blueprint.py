import logging

from flask import Blueprint, request

from dgp_oauth2.lib import Verifyer

from .models import Models
from .controllers import Controllers

from .config import db_connection_string

def list_manager_blueprint(verifyer_args=None, enable_mock_oauth=None): #noqa
    """Create blueprint.
    """
    models = Models(db_connection_string)
    controllers = Controllers(models)

    # Create instance
    blueprint = Blueprint('budgetkey_list_manager', 'budgetkey_list_manager')

    verifyer = Verifyer(**verifyer_args)

    PERMISSION_DENIED = dict(success=False, error='permission denied'), 403

    def get_permissions():
        token = request.headers.get('auth-token') or request.values.get('jwt')
        permissions = verifyer.extract_permissions(token)
        if not permissions and enable_mock_oauth:
            logging.warning("Failed to verify permissions, continuing with mock permissions")
            if token:
                permissions = {"userid": token}
            else:
                permissions = False
        return permissions

    def store_item():
        permissions = get_permissions()
        if permissions is False:
            return PERMISSION_DENIED
        list_name = request.values.get('list')
        update_self = request.values.get('self')
        body = request.get_json()
        if None in (list_name, body):
            return dict(success=False, error='missing required parameter'), 400
        if update_self:
            return controllers.store_list(permissions, list_name, body)
        else:
            return controllers.store_item(permissions, list_name, body)

    def read_():
        permissions = get_permissions()
        if permissions is False:
            return PERMISSION_DENIED
        list_name = request.values.get('list')
        items = bool(request.values.get('items'))
        return controllers.get(permissions, list_name, items)

    def delete_():
        permissions = get_permissions()
        if permissions is False:
            return PERMISSION_DENIED
        list_name = request.values.get('list')
        item_id = request.values.get('item_id')
        if None in (list_name, item_id):
            return dict(success=False, error='missing required parameter'), 400
        if item_id == 'all':
            return controllers.delete_all(permissions, list_name)
        else:
            return controllers.delete(permissions, item_id)

    # Register routes
    blueprint.add_url_rule(
        '/', 'put', store_item, methods=['PUT'])
    blueprint.add_url_rule(
        '/', 'delete', delete_, methods=['DELETE'])
    blueprint.add_url_rule(
        '/', 'get', read_, methods=['GET'])

    # Return blueprint
    return blueprint
