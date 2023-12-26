from .consts import (
    LISTNAME, LISTNAME2, LISTNAME3, USERID, USERID2, ITEM, ITEMS, LISTKIND,
    LISTMETA, LISTNOMETA, LISTMETA_V3, CONTROLLERS_OUTITEMS, MOCK_UUID, time_checker, setup_db, mock_uuid
)

import os
import json
import datetime

from flask import Flask

BLUEPRINT_SCRIPT = [
    ('put', dict(list=LISTNAME), ITEM, dict(id=1, list_id=1, list_name=LISTNAME, **ITEM)),
    *[
        ('put', dict(list=LISTNAME), item, dict(id=i + 1, list_id=1, list_name=LISTNAME, **item))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list=LISTNAME, items='yes'), None,
     dict(id=1, items=CONTROLLERS_OUTITEMS, name=LISTNAME, **LISTNOMETA, user_id=USERID)),
    ('delete', dict(list=LISTNAME, item_id=2), None, dict(success=True)),
    ('get', dict(list=LISTNAME, items='true'), None,
     dict(id=1, name=LISTNAME, items=[CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]], **LISTNOMETA, user_id=USERID)),
    ('delete', dict(list=LISTNAME, item_id='all'), None, dict(success=True)),
    ('get', dict(list=LISTNAME), None, dict(success=False, name=LISTNAME, user_id=USERID)),
    ('put', dict(list=LISTNAME2, self=True), {'title': 'stub', 'properties': [1, 2, 3]},
        dict(id=2, name=LISTNAME2, user_id=USERID, title='stub', properties=[1, 2, 3], kind=None, visibility=0)),
    ('put', dict(list=LISTNAME2, self=True), LISTMETA, dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA)),
    ('get', dict(list=LISTNAME2), None, dict(id=2, name=LISTNAME2, **LISTMETA, user_id=USERID)),
    ('put', dict(list=LISTNAME2), ITEM, dict(id=4, list_id=2, list_name=LISTNAME2, **ITEM)),
    ('put', dict(), None, dict(success=False, error='missing required parameter'), dict(expected_status=415)),
    ('put', dict(list=LISTNAME3), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=415)),
    ('put', dict(list=LISTNAME3), ITEM, dict(id=5, list_id=3, list_name=LISTNAME3, **ITEM)),
    ('get', dict(items=True), None, [
        dict(id=4, list_id=2, **ITEM),
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(items=True, kind=LISTKIND), None, [
        dict(id=4, list_id=2, **ITEM),
    ]),
    ('get', dict(), None, [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA),
        dict(id=3, name=LISTNAME3, user_id=USERID, **LISTNOMETA),
    ]),
    ('get', dict(kind=LISTKIND), None, [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA),
    ]),
    ('get', dict(kind=LISTKIND, user_id=USERID), None, [], dict(user_id=USERID2)),
    ('put', dict(list=LISTNAME2, self=True), LISTMETA_V3, dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA_V3)),
    ('get', dict(kind=LISTKIND, user_id=USERID), None, [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA_V3),
    ], dict(user_id=USERID2)),
    ('get', dict(kind=LISTKIND, user_id=USERID), None, [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA_V3),
    ], dict(user_id=None)),

    ('delete', dict(list=LISTNAME2, item_id='all'), None, dict(success=True)),
    ('get', dict(items=True), None, [
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(), None, [dict(id=3, name=LISTNAME3, user_id=USERID, **LISTNOMETA)]),
    ('delete', dict(list=LISTNAME3), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=400)),
    ('delete', dict(item_id=6), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=400)),
    ('delete', dict(), None, dict(success=False, error='missing required parameter'),
        dict(expected_status=400)),
    ('delete', dict(list=LISTNAME3, item_id='all'), None, dict(success=True)),
    ('get', dict(), None, []),
    ('put', dict(list=LISTNAME), ITEM, dict(id=6, list_id=4, list_name=LISTNAME, **ITEM), dict(user_id=USERID2)),
    ('put', dict(list=LISTNAME), ITEMS[1], dict(success=False, error='permission denied'),
     dict(user_id=None, expected_status=403)),
    ('get', dict(list=LISTNAME), None, dict(success=False, error='permission denied'),
     dict(user_id=None, expected_status=403)),
    ('delete', dict(list=LISTNAME3, item_id='all'), None, dict(success=False, name=LISTNAME3, user_id=USERID)),
    ('delete', dict(list=LISTNAME3, item_id=6), None, dict(success=False)),
    ('delete', dict(list=LISTNAME3, item_id=61), None, dict(success=False)),
    ('delete', dict(list=LISTNAME3, item_id=61), None, dict(success=False), dict(user_id=USERID2)),
    ('delete', dict(list=LISTNAME3, item_id='all'), None, dict(success=False, error='permission denied'),
        dict(user_id=None, expected_status=403)),
    ('delete', dict(list=LISTNAME3, item_id=6), None, dict(success=False, error='permission denied'),
        dict(user_id=None, expected_status=403)),
    ('get', dict(list=LISTNAME, items=True), None,
     dict(id=4, name=LISTNAME, items=[dict(id=6, list_id=4, **ITEM)], **LISTNOMETA, user_id=USERID2),
     dict(user_id=USERID2)),
    ('put', dict(), ITEM, dict(id=7, list_id=5, list_name=MOCK_UUID, **ITEM)),

    ('put', dict(list=LISTNAME), ITEM, dict(id=8, list_id=6, list_name=LISTNAME, **ITEM)),
    (
        'get', dict(list=LISTNAME, items=True), None,
        dict(id=4, name=LISTNAME, items=[dict(id=6, list_id=4, **ITEM)], **LISTNOMETA, user_id=USERID2),
        dict(user_id=USERID2)
    ),
    (
        'get', dict(list=LISTNAME, items=True), None,
        dict(id=6, name=LISTNAME, items=[dict(id=8, list_id=6, **ITEM)], **LISTNOMETA, user_id=USERID),
        dict(user_id=USERID)
    ),
    (
        'get', dict(list=LISTNAME, items=True, user_id=USERID), None,
        dict(success=False, name=LISTNAME, user_id=USERID), dict(user_id=USERID2)
    ),
    (
        'get', dict(list=LISTNAME, items=True, user_id=USERID2), None,
        dict(success=False, name=LISTNAME, user_id=USERID2), dict(user_id=USERID)
    ),
    (
        'put', dict(list=LISTNAME, self=True), LISTMETA,
        dict(id=4, user_id=USERID2, name=LISTNAME, **LISTMETA), dict(user_id=USERID2)
    ),
    ('get', dict(list=LISTNAME, items=True, user_id=USERID2), None, dict(
        id=4, name=LISTNAME, items=[dict(id=6, list_id=4, **ITEM)], **LISTMETA, user_id=USERID2
    ), dict(user_id=USERID)),
    ('get', dict(list=LISTNAME, items=True, user_id=USERID2), None, dict(
        id=4, name=LISTNAME, items=[dict(id=6, list_id=4, **ITEM)], **LISTMETA, user_id=USERID2
    ), dict(user_id=None)),
    (
        'get', dict(list=LISTNAME, items=True, user_id=None), None, dict(success=False, error='permission denied'),
        dict(user_id=None, expected_status=403)),
    (
        'get', dict(list=None, items=True, user_id=USERID2), None, dict(success=False, name=None, user_id=USERID2),
        dict(user_id=None)
    ),
    (
        'get', dict(list=None, items=True, user_id=USERID2, kind=LISTKIND), None, [],
        dict(user_id=None)
    ),
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


def run():
    os.environ['PRIVATE_KEY'] = 'stub'
    setup_db('blueprint', env=True)

    from budgetkey_api.list_manager import blueprint
    from budgetkey_api.list_manager import models

    mock_uuid(models)

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
