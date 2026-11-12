import os

from apisql import apisql_blueprint
from .caching import add_cache_header, add_public_cors_header


MAX_ROWS = int(os.environ.get('MAX_ROWS', 1000))
EXTERNAL_ADDRESS = os.environ.get('EXTERNAL_ADDRESS')


def setup_query(app, cache):
    bp = apisql_blueprint(connection_string=os.environ['DATABASE_READONLY_URL'],
                          max_rows=MAX_ROWS, debug=False, cache=cache,
                          external_url=f'https://{EXTERNAL_ADDRESS}/api')
    # Public and credential-less, and cached for an hour by nginx in front of us: a wildcard origin keeps a copy
    # cached from a request without an Origin (server-side rendering, curl) usable by every browser
    add_public_cors_header(bp)
    add_cache_header(bp, 3600)
    app.register_blueprint(bp, url_prefix='/api/')
    return bp
