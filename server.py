import os

from budgetkey_api.flask_app import create_flask_app

app = create_flask_app(os.environ.get('SERVICES'))

if __name__ == '__main__':
    app.run()
else:
    import logging
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('SERVER STARTING')
