from flask import request
from flask_cors.core import FLASK_CORS_EVALUATED


def add_public_cors_header(app):
    # The app-wide CORS setup echoes the request's Origin (as it must, with credentials enabled).
    # A shared cache in front of us that ignores 'Vary: Origin' would then pin the first response
    # it sees - including one fetched with no Origin at all, i.e. with no CORS headers - and serve
    # it to every browser. For public, credential-less responses a wildcard is valid for any origin,
    # so a cached copy is always usable.
    def func(response):
        if request.method != 'OPTIONS':  # leave preflights to the app-wide CORS handling
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers.pop('Access-Control-Allow-Credentials', None)
            # Keep the app-wide handler from adding a second, origin-specific header
            setattr(response, FLASK_CORS_EVALUATED, True)
        return response
    app.after_request(func)


def add_cache_header(app, max_age):
    def func(response):
        if max_age > 0 and response.status_code == 200:
            response.cache_control.max_age = max_age
        if max_age == 0:
            response.cache_control.no_cache = True
        return response
    app.after_request(func)
