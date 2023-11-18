import os

from budgetkey_api.list_manager.blueprint import list_manager_blueprint


def setup_list_manager(app):
    auth_endpoint = f'https://{os.environ["EXTERNAL_ADDRESS"]}/auth/'
    verifyer_args = dict(auth_endpoint=auth_endpoint)

    app.register_blueprint(
        list_manager_blueprint(verifyer_args=verifyer_args),
        url_prefix='/lists/'
    )
