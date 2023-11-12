import os

from apisql import apisql_blueprint


def setup_query(app):
    app.register_blueprint(
        apisql_blueprint(
            connection_string=os.environ['DATABASE_READONLY_URL'],
            max_rows=20000, debug=False
        ),
        url_prefix='/api/db/'
    )
