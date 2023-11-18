import os

from budgetkey_api.list_manager.blueprint import list_manager_blueprint


def setup_list_manager(app):
    verifyer_args = dict(public_key=os.environ['PUBLIC_KEY'])

    app.register_blueprint(
        list_manager_blueprint(verifyer_args=verifyer_args),
        url_prefix='/lists/'
    )
