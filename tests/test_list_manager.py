import os
import json

LISTNAME = 'saved-searches'
LISTNAME2 = 'my-second-list'
LISTNAME3 = 'my-third-list'
USERID = 'user-id-123'
USERID2 = 'user-id-456'
ITEM = {"title": "item1", "url": "http://example.com/1", "properties": {"a": 1, "b": [2, 1]}}
ITEMS = [
    {"title": "item1", "url": "http://example.com/1", "properties": {"a": 1, "b": [1, 2]}},
    {"title": "item2", "url": "http://example.com/2", "properties": {"a": 2, "b": [3, 4]}},
    {"title": "item3", "url": "http://example.com/3", "properties": {"a": 3, "b": [5, 6]}}
]


def setup_db(key, env=False):
    filename = f'tests/temp/test_list_manager_{key}.sqlite3'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        os.unlink(filename)
    connection_string = f'sqlite:///{filename}'
    if env:
        os.environ['DATABASE_PRIVATE_URL'] = connection_string
    else:
        from budgetkey_api.list_manager.models import Models
        return Models(connection_string)


def single_test(obj, method, kwargs, expected):
    def func():
        print('Testing', method, kwargs, expected)
        actual = getattr(obj, method)(**kwargs)
        assert actual == expected
    return func


MODEL_OUTITEMS = [
    dict(id=i + 1, list_id=1, **item)
    for i, item in enumerate(ITEMS)
]

MODELS_SCRIPT = [
    ('get_list', dict(list_name=LISTNAME, user_id=USERID), None),
    ('create_list', dict(list_name=LISTNAME, user_id=USERID), dict(id=1, name=LISTNAME, user_id=USERID)),
    ('add_item', dict(list_name=LISTNAME, user_id=USERID, item=ITEM), dict(id=1, list_id=1, **ITEM)),
    *[
        ('add_item', dict(list_name=LISTNAME, user_id=USERID, item=item), outitem)
        for item, outitem in zip(ITEMS, MODEL_OUTITEMS)
    ],
    ('get_items', dict(list_name=LISTNAME, user_id=USERID), MODEL_OUTITEMS),
    ('delete_item', dict(item_id=2), None),
    ('get_items', dict(list_name=LISTNAME, user_id=USERID), [MODEL_OUTITEMS[0], MODEL_OUTITEMS[2]]),
    ('delete_list', dict(list_id=1), None),
    ('get_items', dict(list_name=LISTNAME, user_id=USERID), []),
    ('create_list', dict(list_name=LISTNAME2, user_id=USERID), dict(id=2, name=LISTNAME2, user_id=USERID)),
    ('create_list', dict(list_name=LISTNAME3, user_id=USERID), dict(id=3, name=LISTNAME3, user_id=USERID)),
    ('get_all_lists', dict(user_id=USERID), [
        dict(id=2, name=LISTNAME2),
        dict(id=3, name=LISTNAME3),
    ]),
    ('get_all_items', dict(user_id=USERID), []),
    ('add_item', dict(list_name=LISTNAME2, user_id=USERID, item=ITEM), dict(id=4, list_id=2, **ITEM)),
    ('add_item', dict(list_name=LISTNAME3, user_id=USERID, item=ITEM), dict(id=5, list_id=3, **ITEM)),
    ('get_all_items', dict(user_id=USERID), [dict(id=4, list_id=2, **ITEM), dict(id=5, list_id=3, **ITEM)]),
    ('delete_list', dict(list_id=2), None),
    ('get_all_items', dict(user_id=USERID), [dict(id=5, list_id=3, **ITEM)]),
    ('get_all_lists', dict(user_id=USERID), [
        dict(id=3, name=LISTNAME3),
    ]),
    ('delete_list', dict(list_id=3), None),
    ('get_all_lists', dict(user_id=USERID), []),
]


def models_tests():
    models = setup_db('models')

    for step, (method, kwargs, expected) in enumerate(MODELS_SCRIPT):
        globals()[f'test_list_manager_models_{step:02d}_{method}'] = single_test(models, method, kwargs, expected)


PERMISSIONS = dict(userid=USERID)
CONTROLLERS_OUTITEMS = [
    dict(id=i + 1, list_id=1, **item)
    for i, item in enumerate(ITEMS)
]
CONTROLLERS_SCRIPT = [
    ('store', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=ITEM), dict(item_id=1, list_id=1)),
    *[
        ('store', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=item), dict(item_id=i + 1, list_id=1))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list_name=LISTNAME, permissions={}, items=False), dict(success=False)),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=False), dict(id=1, items=CONTROLLERS_OUTITEMS)),
    ('delete', dict(item_id=2, permissions={}), dict(success=False)),
    ('delete', dict(item_id=2, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=False), dict(id=1, items=[
        CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]
    ])),
    ('delete_all', dict(list_name=LISTNAME, permissions={}), dict(success=False)),
    ('delete_all', dict(list_name=LISTNAME, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=False), dict(success=False)),
    ('store', dict(list_name=LISTNAME2, permissions=PERMISSIONS, item=ITEM), dict(item_id=4, list_id=2)),
    ('store', dict(list_name=LISTNAME3, permissions={}, item=ITEM), dict(success=False)),
    ('store', dict(list_name=LISTNAME3, permissions=PERMISSIONS, item=ITEM), dict(item_id=5, list_id=3)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True), [
        dict(id=4, list_id=2, **ITEM),
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('delete_all', dict(list_name=LISTNAME2, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True), [
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False), [dict(id=3, name=LISTNAME3)]),
    ('delete_all', dict(list_name=LISTNAME3, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False), []),
]


def controllers_tests():
    from budgetkey_api.list_manager.controllers import Controllers
    models = setup_db('controllers')
    controllers = Controllers(models)

    for step, (method, kwargs, expected) in enumerate(CONTROLLERS_SCRIPT):
        globals()[f'test_list_manager_controllers_{step:02d}_{method}'] = \
            single_test(controllers, method, kwargs, expected)


BLUEPRINT_SCRIPT = [
    ('put', dict(list=LISTNAME), ITEM, dict(item_id=1, list_id=1)),
    *[
        ('put', dict(list=LISTNAME), item, dict(item_id=i + 1, list_id=1))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list=LISTNAME), None, dict(id=1, items=CONTROLLERS_OUTITEMS)),
    ('delete', dict(list=LISTNAME, item_id=2), None, dict(success=True)),
    ('get', dict(list=LISTNAME), None, dict(id=1, items=[CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]])),
    ('delete', dict(list=LISTNAME, item_id='all'), None, dict(success=True)),
    ('get', dict(list=LISTNAME), None, dict(success=False)),
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
    ('get', dict(), None, [dict(id=3, name=LISTNAME3)]),
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
    ('get', dict(list=LISTNAME), None, dict(id=4, items=[dict(id=6, list_id=4, **ITEM)]),
        dict(user_id=USERID2)),
]


def single_request(client, method, kwargs, body, expected, expected_status=200, user_id=USERID):
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
            assert actual == expected
    return func


def blueprint_tests():
    os.environ['PRIVATE_KEY'] = 'stub'
    setup_db('blueprint', env=True)

    from budgetkey_api.list_manager import blueprint
    from flask import Flask

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


models_tests()
controllers_tests()
blueprint_tests()
