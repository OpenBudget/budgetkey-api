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


def test_datarecords_upstream_failure(tmp_path, monkeypatch):
    from budgetkey_api.modules import datarecords

    def fake_get(url, **kwargs):
        raise ConnectionError('boom')

    monkeypatch.setattr(datarecords.requests, 'get', fake_get)

    client = make_client(tmp_path)
    resp = client.get('/api/datarecords/intervention')
    assert resp.status_code == 502
