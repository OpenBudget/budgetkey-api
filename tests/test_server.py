import dotenv

dotenv.load_dotenv('tests/sample.env')


def test_server_init():
    from budgetkey_api.flask_app import create_flask_app
    app = create_flask_app(session_file_dir='./tests/temp/sessions', cache_dir='./tests/temp/cache')
    assert app is not None
