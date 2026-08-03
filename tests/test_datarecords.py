import dotenv

dotenv.load_dotenv('tests/sample.env')


def make_client(tmp_path):
    from budgetkey_api.flask_app import create_flask_app

    app = create_flask_app(session_file_dir=str(tmp_path / 'sessions'), cache_dir=str(tmp_path / 'cache'),
                           services='none')
    app.config.update({'TESTING': True})
    app.testing = True
    return app.test_client()


def test_datarecords_bad_key(tmp_path):
    client = make_client(tmp_path)
    resp = client.get('/api/datarecords/no_such_key')
    assert resp.status_code == 404


def test_datarecords_fetches_and_caches(tmp_path, monkeypatch):
    from budgetkey_api.modules import datarecords

    calls = []

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {'result': [{'key': 'subject::foo'}]}

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse()

    monkeypatch.setattr(datarecords.requests, 'get', fake_get)

    client = make_client(tmp_path)
    for _ in range(2):
        resp = client.get('/api/datarecords/subject')
        assert resp.status_code == 200
        assert resp.json == {'result': [{'key': 'subject::foo'}]}
        assert resp.headers['Cache-Control'] == f'max-age={datarecords.TIMEOUT}'

    # Second call is served from the cache
    assert calls == [f'{datarecords.DATARECORDS_URL}/subject']


def test_datarecords_cors_is_wildcard(tmp_path, monkeypatch):
    from budgetkey_api.modules import datarecords

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {'result': []}

    monkeypatch.setattr(datarecords.requests, 'get', lambda url, **kwargs: FakeResponse())

    client = make_client(tmp_path)

    # A wildcard regardless of (or without) an Origin, so that a cached copy is valid for everyone
    for headers in ({}, {'Origin': 'https://example.com'}, {'Origin': 'http://localhost:4200'}):
        resp = client.get('/api/datarecords/subject', headers=headers)
        assert resp.status_code == 200
        assert resp.headers.get_all('Access-Control-Allow-Origin') == ['*']
        assert 'Access-Control-Allow-Credentials' not in resp.headers
        assert 'Origin' not in resp.headers.get('Vary', '')

    # Error responses are reachable cross-origin too
    resp = client.get('/api/datarecords/no_such_key', headers={'Origin': 'https://example.com'})
    assert resp.status_code == 404
    assert resp.headers.get_all('Access-Control-Allow-Origin') == ['*']

    # Preflights still go through the app-wide CORS handling
    resp = client.options('/api/datarecords/subject',
                          headers={'Origin': 'https://example.com', 'Access-Control-Request-Method': 'GET'})
    assert resp.status_code == 200
    assert resp.headers['Access-Control-Allow-Origin'] == 'https://example.com'
    assert 'GET' in resp.headers['Access-Control-Allow-Methods']


def test_datarecords_upstream_failure(tmp_path, monkeypatch):
    from budgetkey_api.modules import datarecords

    def fake_get(url, **kwargs):
        raise ConnectionError('boom')

    monkeypatch.setattr(datarecords.requests, 'get', fake_get)

    client = make_client(tmp_path)
    resp = client.get('/api/datarecords/intervention')
    assert resp.status_code == 502
