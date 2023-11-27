import os

from budgetkey_api.list_manager.blueprint import list_manager_blueprint
from .caching import add_cache_header


def setup_list_manager(app):
    verifyer_args = dict(public_key=os.environ['PUBLIC_KEY'])
    lm = list_manager_blueprint(verifyer_args=verifyer_args)
    add_cache_header(lm, 0)
    app.register_blueprint(lm, url_prefix='/lists/')
