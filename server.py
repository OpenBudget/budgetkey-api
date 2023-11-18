import os

from budgetkey_api.flask_app import create_flask_app

app = create_flask_app(services=os.environ.get('SERVICES'))

if __name__ == '__main__':
    app.run()
else:
    import logging
    import sys
    gunicorn_error_logger = logging.getLogger('gunicorn.error')

    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('SERVER STARTING')

    dgp_auth_logger = logging.getLogger('dgp-oauth2')
    dgp_auth_logger.setLevel(logging.DEBUG)
    dgp_auth_logger.handlers.extend(gunicorn_error_logger.handlers)
