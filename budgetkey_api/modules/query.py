import os

from apisql import apisql_blueprint


MAX_ROWS = int(os.environ.get('MAX_ROWS', 1000))


def setup_query(app, cache):
    app.register_blueprint(
        apisql_blueprint(connection_string=os.environ['DATABASE_READONLY_URL'],
                         max_rows=MAX_ROWS, debug=False, cache=cache),
        url_prefix='/api/'
    )
