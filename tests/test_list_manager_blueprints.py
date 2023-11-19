from .consts import (
    LISTNAME, LISTNAME2, LISTNAME3, USERID, USERID2, ITEM, ITEMS, LISTMETA, CONTROLLERS_OUTITEMS, time_checker, setup_db
)

import os
import json
import datetime

from flask import Flask

BLUEPRINT_SCRIPT = [
    ('put', dict(list=LISTNAME), ITEM, dict(item_id=1, list_id=1)),
    *[
        ('put', dict(list=LISTNAME), item, dict(item_id=i + 1, list_id=1))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list=LISTNAME, items='yes'), None,
     dict(id=1, items=CONTROLLERS_OUTITEMS, name=LISTNAME, title=None, properties=None)),
    ('delete', dict(list=LISTNAME, item_id=2), None, dict(success=True)),
    ('get', dict(list=LISTNAME, items='true'), None,
     dict(id=1, name=LISTNAME, items=[CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]], title=None, properties=None)),
    ('delete', dict(list=LISTNAME, item_id='all'), None, dict(success=True)),
    ('get', dict(list=LISTNAME), None, dict(success=False)),
    ('put', dict(list=LISTNAME2, self=True), {'title': 'stub', 'properties': [1, 2, 3]}, dict(id=2)),
    ('put', dict(list=LISTNAME2, self=True), LISTMETA, dict(id=2)),
    ('get', dict(list=LISTNAME2), None, dict(id=2, name=LISTNAME2, **LISTMETA)),
    ('put', dict(list=LISTNAME2), ITEM, dict(item_id=4, list_id=2)),
    ('put', dict(), None, dict(success=False, error='missing required parameter'), dict(expected_status=415)),
    ('put', dict(), ITEM, dict(success=False, error='missing required parameter'), dict(expected_status=400)),
    ('put', dict(list=LISTNAME3), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=415)),
    ('put', dict(list=LISTNAME3), ITEM, dict(item_id=5, list_id=3)),
    ('get', dict(items=True), None, [
        dict(id=4, list_id=2, **ITEM),
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('delete', dict(list=LISTNAME2, item_id='all'), None, dict(success=True)),
    ('get', dict(items=True), None, [
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(), None, [dict(id=3, name=LISTNAME3, title=None, properties=None)]),
    ('delete', dict(list=LISTNAME3), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=400)),
    ('delete', dict(item_id=6), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=400)),
    ('delete', dict(), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=400)),
    ('delete', dict(list=LISTNAME3, item_id='all'), None, dict(success=True)),
    ('get', dict(), None, []),
    ('put', dict(list=LISTNAME), ITEM, dict(item_id=6, list_id=4), dict(user_id=USERID2)),
    ('put', dict(list=LISTNAME), ITEMS[1], dict(success=False, error='permission denied'), dict(user_id=None)),
    ('get', dict(list=LISTNAME), None, dict(success=False, error='permission denied'), dict(user_id=None)),
    ('delete', dict(list=LISTNAME3, item_id='all'), None, dict(success=False)),
    ('delete', dict(list=LISTNAME3, item_id=6), None, dict(success=False)),
    ('delete', dict(list=LISTNAME3, item_id=61), None, dict(success=False)),
    ('delete', dict(list=LISTNAME3, item_id=61), None, dict(success=False), dict(user_id=USERID2)),
    ('delete', dict(list=LISTNAME3, item_id='all'), None, dict(success=False, error='permission denied'),
        dict(user_id=None)),
    ('delete', dict(list=LISTNAME3, item_id=6), None, dict(success=False, error='permission denied'),
        dict(user_id=None)),
    ('get', dict(list=LISTNAME, items=True), None,
     dict(id=4, name=LISTNAME, items=[dict(id=6, list_id=4, **ITEM)], title=None, properties=None),
     dict(user_id=USERID2)),
]


def single_request(client, method, kwargs, body, expected, expected_status=200, user_id=USERID):
    now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)

    def func():
        print('Testing', method, kwargs, expected)
        client_method = getattr(client, method)
        params = dict()
        good_status_code = expected_status
        if user_id:
            params['headers'] = {'auth-token': user_id}
        else:
            good_status_code = 403
        if kwargs:
            params['query_string'] = kwargs
        if body:
            params['json'] = body
        response = client_method('/lists/', **params)
        assert response.status_code == good_status_code
        if response.status_code in (200, 400, 404, 403):
            actual = json.loads(response.data)
            time_checker(now, actual)
            assert actual == expected
    return func


os.environ['PRIVATE_KEY'] = 'stub'
setup_db('blueprint', env=True)


def run():
    from budgetkey_api.list_manager import blueprint

    app = Flask('test')
    app.config.update({
        "TESTING": True,
    })
    app.testing = True
    app.register_blueprint(blueprint.list_manager_blueprint(dict(public_key='stub'), enable_mock_oauth=True),
                           url_prefix='/lists/')
    client = app.test_client()

    for step, (method, kwargs, body, expected, *args) in enumerate(BLUEPRINT_SCRIPT):
        if args:
            args = args[0]
        else:
            args = {}
        globals()[f'test_list_manager_blueprint_{step:02d}_{method}'] = \
            single_request(client, method, kwargs, body, expected, **args)


run()
