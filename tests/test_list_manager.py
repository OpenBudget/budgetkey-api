import os
import json

LISTNAME = 'saved-searches'
USERID = 'user-id-123'
ITEM = {"title": "item1", "url": "http://example.com/1", "properties": {"a":1,"b":[2,1]}}
ITEMS = [
    {"title": "item1", "url": "http://example.com/1", "properties": {"a":1,"b":[1,2]}},
    {"title": "item2", "url": "http://example.com/2", "properties": {"a":2,"b":[3,4]}},
    {"title": "item3", "url": "http://example.com/3", "properties": {"a":3,"b":[5,6]}}
]

def setup_db(models, key, env=False):
    filename = f'tests/temp/test_list_manager_{key}.sqlite3'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        os.unlink(filename)
    connection_string = f'sqlite:///{filename}'
    if env:
        os.environ['DATABASE_PRIVATE_URL'] = connection_string
    else:
        models.setup_engine(connection_string)

def single_test(obj, method, kwargs, expected):
    def func():
        print('Testing', method, kwargs, expected)
        actual = getattr(obj, method)(**kwargs)
        assert actual == expected
    return func

MODEL_OUTITEMS = [
    dict(id=i+1, list_id=1, **item)
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
]

def models_tests():
    from budgetkey_api.list_manager import models
    setup_db(models, 'models')

    for step, (method, kwargs, expected) in enumerate(MODELS_SCRIPT):
        globals()[f'test_list_manager_models_{step:02d}_{method}'] = single_test(models, method, kwargs, expected)

'store', 'get', 'delete', 'delete_all'

PERMISSIONS = dict(userid=USERID)
CONTROLLERS_OUTITEMS = [
    dict(id=i+1, list_id=1, **item)
    for i, item in enumerate(ITEMS)
]
CONTROLLERS_SCRIPT = [
    ('store', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=ITEM), dict(item_id=1, list_id=1)),
    *[
        ('store', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=item), dict(item_id=i+1, list_id=1))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS), dict(id=1, items=CONTROLLERS_OUTITEMS)),
    ('delete', dict(item_id=2, permissions=PERMISSIONS), True),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS), dict(id=1, items=[CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]])),
    ('delete_all', dict(list_name=LISTNAME, permissions=PERMISSIONS), True),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS), dict(id=1, items=[])),
]


def controllers_tests():
    from budgetkey_api.list_manager import controllers, models
    setup_db(models, 'controllers')

    for step, (method, kwargs, expected) in enumerate(CONTROLLERS_SCRIPT):
        globals()[f'test_list_manager_controllers_{step:02d}_{method}'] = single_test(controllers, method, kwargs, expected)


BLUEPRINT_SCRIPT = [
    ('put', dict(list=LISTNAME), ITEM, dict(item_id=1, list_id=1)),
    *[
        ('put', dict(list=LISTNAME), item, dict(item_id=i+1, list_id=1))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list=LISTNAME), None, dict(id=1, items=CONTROLLERS_OUTITEMS)),
    ('delete', dict(list=LISTNAME, item_id=2), None, True),
    ('get', dict(list=LISTNAME), None, dict(id=1, items=[CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]])),
    ('delete', dict(list=LISTNAME, item_id='all'), None, True),
    ('get', dict(list=LISTNAME), None, dict(id=1, items=[])),
]


def single_request(client, method, kwargs, body, expected):
    def func():
        print('Testing', method, kwargs, expected)
        client_method = getattr(client, method)
        params = dict(headers={'auth-token': USERID})
        if kwargs:
            params['query_string'] = kwargs
        if body:
            params['json'] = body
        response = client_method('/list/', **params)
        assert response.status_code == 200
        actual = json.loads(response.data)
        assert actual == expected
    return func


def blueprint_tests():
    os.environ['PRIVATE_KEY'] = 'stub'
    setup_db(None, 'blueprint', env=True)

    from budgetkey_api.list_manager import blueprint
    from flask import Flask

    app = Flask('test')
    app.config.update({
        "TESTING": True,
    })
    app.testing = True
    app.register_blueprint(blueprint.list_manager_blueprint(dict(public_key='stub'), enable_mock_oauth=True),
                            url_prefix='/list/')
    client = app.test_client()

    for step, (method, kwargs, body, expected) in enumerate(BLUEPRINT_SCRIPT):
        globals()[f'test_list_manager_blueprint_{step:02d}_{method}'] = single_request(client, method, kwargs, body, expected)


models_tests()
controllers_tests()
blueprint_tests()