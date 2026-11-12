"""CORS headers on the public query API, which nginx caches for an hour whatever the request's Origin."""
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS


def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_READONLY_URL', 'sqlite:///' + str(tmp_path / 'db.sqlite3'))
    from budgetkey_api.modules.query import setup_query
    app = Flask(__name__)
    CORS(app, supports_credentials=True)  # as in create_flask_app
    cache = Cache(config={'CACHE_TYPE': 'NullCache'})
    cache.init_app(app)
    setup_query(app, cache)
    return app.test_client()


def test_query_responses_allow_every_origin(tmp_path, monkeypatch):
    c = client(tmp_path, monkeypatch)
    # Without an Origin (server-side rendering, curl): still a wildcard, so the cached copy works in browsers
    resp = c.get('/api/query?query=select 1 as x')
    assert resp.status_code == 200 and resp.headers['Cache-Control'] == 'max-age=3600'
    assert resp.headers['Access-Control-Allow-Origin'] == '*'
    # With one: the same wildcard, never the echoed origin with credentials
    resp = c.get('/api/query?query=select 1 as x', headers={'Origin': 'https://next.obudget.org'})
    assert resp.headers['Access-Control-Allow-Origin'] == '*'
    assert 'Access-Control-Allow-Credentials' not in resp.headers
    assert resp.headers.get_all('Access-Control-Allow-Origin') == ['*']


def test_preflight_is_left_to_the_app_cors(tmp_path, monkeypatch):
    c = client(tmp_path, monkeypatch)
    headers = {'Origin': 'http://127.0.0.1:4200', 'Access-Control-Request-Method': 'GET'}
    resp = c.options('/api/query?query=select 1', headers=headers)
    assert resp.headers['Access-Control-Allow-Origin'] == 'http://127.0.0.1:4200'
