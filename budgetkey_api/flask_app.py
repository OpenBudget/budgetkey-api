import logging
import time


from flask import Flask, g as app_ctx, request, current_app
from flask_cors import CORS
from flask_caching import Cache
from flask_session import Session

from .modules import setup_search, setup_query, setup_auth


def add_cache_header(response):
    response.cache_control.max_age = 600
    return response


def logging_before():
    # Store the start time for the request
    app_ctx.start_time = time.perf_counter()


def logging_after(response):
    # Get total time in milliseconds
    total_time = time.perf_counter() - app_ctx.start_time
    time_in_ms = int(total_time * 1000)
    # Log the time taken for the endpoint
    if time_in_ms > 5000:
        current_app.logger.warning('SLOW: %-5s ms %4s %s %s', time_in_ms, request.method, request.path, dict(request.args))
    elif time_in_ms > 2000:
        current_app.logger.info('SLOW: %-5s ms %4s %s %s', time_in_ms, request.method, request.path, dict(request.args))
    return response


def create_flask_app(session_file_dir=None, cache_dir=None):
    app = Flask(__name__)
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    CORS(app, supports_credentials=True)

    config = {
        "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 600,
        "CACHE_DIR": cache_dir or "/var/run/budgetkey-api/cache",
        "CACHE_THRESHOLD": 100,
        "CACHE_OPTIONS": {
            "mode": 0o700
        },
    }
    cache = Cache(config=config)
    cache.init_app(app)

    sess = Session()
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = session_file_dir or '/var/run/budgetkey-api/sessions'
    app.config['SECRET_KEY'] = '-'
    sess.init_app(app)

    setup_search(app)
    setup_query(app, cache)
    setup_auth(app)

    app.after_request(add_cache_header)
    app.before_request(logging_before)
    app.after_request(logging_after)

    return app
