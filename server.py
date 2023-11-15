import logging

from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_session import Session

from modules import setup_search, setup_query, setup_auth


app = Flask(__name__)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

CORS(app, supports_credentials=True)

config = {
    "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 600,
    "CACHE_DIR": "/var/run/budgetkey-api/cache",
    "CACHE_THRESHOLD": 100,
    "CACHE_OPTIONS": {
        "mode": 0o700
    },
}
cache = Cache(config=config)
cache.init_app(app)


sess = Session()
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/var/run/budgetkey-api/sessions'
app.config['SECRET_KEY'] = '-'
sess.init_app(app)


setup_search(app)
setup_query(app, cache)
setup_auth(app)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 600
    return response


if __name__ == '__main__':
    app.run()
else:
    import logging
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('SERVER STARTING')
