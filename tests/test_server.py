import time
from flask import Flask
import dotenv

dotenv.load_dotenv('tests/sample.env')


def wait(seconds):
    time.sleep(seconds)
    return 'OK'


def test_server_init():
    from budgetkey_api.flask_app import create_flask_app

    app: Flask = create_flask_app(session_file_dir='./tests/temp/sessions', cache_dir='./tests/temp/cache')
    assert app is not None

    app.config.update({
        "TESTING": True,
    })
    app.testing = True
    app.add_url_rule('/wait/<int:seconds>', view_func=wait)

    client = app.test_client()
    assert client.get('/').status_code == 404

    resp = client.get('/lists/')
    assert resp.status_code == 403

    resp = client.get('/wait/1')
    assert resp.status_code == 200

    resp = client.get('/wait/3')
    assert resp.status_code == 200

    resp = client.get('/wait/6')
    assert resp.status_code == 200
