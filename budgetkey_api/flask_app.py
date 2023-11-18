import logging
import time
import os

from flask import Flask, g as app_ctx, request, current_app
from flask_cors import CORS
from flask_caching import Cache


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
    if time_in_ms > 500:
        msg = 'SLOW: %-5s ms %4s %s %s' % (
            time_in_ms, request.method, request.path, dict(request.args)
        )
    if time_in_ms > 5000:
        current_app.logger.warning(msg)
    elif time_in_ms > 2000:
        current_app.logger.info(msg)
    elif time_in_ms > 500:
        current_app.logger.debug(msg)
    return response


def create_flask_app(session_file_dir=None, cache_dir=None, services=None):
    app = Flask(__name__)
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    CORS(app, supports_credentials=True)

    app.secret_key = os.environ['SECRET_KEY']

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

    session = Session()
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = session_file_dir or '/var/run/budgetkey-api/sessions'
    session.init_app(app)

    services = services or 'auth,es,lists,db'
    services = services.split(',')

    if 'es' in services:
        log.info("Setting up ES")
        from .modules.search import setup_search
        setup_search(app)
        log.info("ES setup complete")
    if 'db' in services:
        log.info("Setting up DB")
        from .modules.query import setup_query
        setup_query(app, cache)
        log.info("DB setup complete")
    if 'auth' in services:
        log.info("Setting up Auth")
        from .modules.auth import setup_auth
        setup_auth(app, cache)
        log.info("Auth setup complete")
    if 'lists' in services:
        log.info("Setting up Lists")
        from .modules.list_manager import setup_list_manager
        setup_list_manager(app)
        log.info("Lists setup complete")

    app.after_request(add_cache_header)
    app.before_request(logging_before)
    app.after_request(logging_after)

    return app
