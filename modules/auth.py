import os

from dgp_oauth2 import make_blueprint as auth_blueprint


def setup_auth(app):
    app.register_blueprint(
        auth_blueprint(os.environ.get('EXTERNAL_ADDRESS'),
                       db_connection_string=os.environ['DATABASE_PRIVATE_URL']),
        url_prefix='/api/auth/'
    )
