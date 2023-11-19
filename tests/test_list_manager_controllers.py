import datetime

from budgetkey_api.list_manager.controllers import Controllers
from .consts import (
    LISTNAME, LISTNAME2, LISTNAME3, USERID, ITEM, ITEMS, LISTMETA, CONTROLLERS_OUTITEMS, time_checker, setup_db
)


def single_test(obj, method, kwargs, expected):
    now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)

    def func():
        print('Testing', method, kwargs, expected)
        actual = getattr(obj, method)(**kwargs)
        time_checker(now, actual)
        assert actual == expected
    return func


PERMISSIONS = dict(userid=USERID)
CONTROLLERS_SCRIPT = [
    ('store_item', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=ITEM), dict(item_id=1, list_id=1)),
    *[
        ('store_item', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=item), dict(item_id=i + 1, list_id=1))
        for i, item in enumerate(ITEMS)
    ],
    ('get', dict(list_name=LISTNAME, permissions={}, items=False), dict(success=False)),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=True),
     dict(id=1, name=LISTNAME, items=CONTROLLERS_OUTITEMS, title=None, properties=None)),
    ('delete', dict(item_id=2, permissions={}), dict(success=False)),
    ('delete', dict(item_id=2, permissions=PERMISSIONS), dict(success=True)),
    ('delete', dict(item_id=212, permissions=PERMISSIONS), dict(success=False)),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=True), dict(id=1, name=LISTNAME, items=[
        CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]
    ], title=None, properties=None)),
    ('delete_all', dict(list_name=LISTNAME, permissions={}), dict(success=False)),
    ('delete_all', dict(list_name=LISTNAME, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=False), dict(success=False)),
    ('store_list', dict(list_name=LISTNAME2, permissions=PERMISSIONS, rec=LISTMETA), dict(id=2)),
    ('get', dict(list_name=LISTNAME2, permissions=PERMISSIONS, items=False),
     dict(id=2, name=LISTNAME2, **LISTMETA)),
    ('get', dict(list_name=LISTNAME2, permissions=PERMISSIONS, items=True),
     dict(id=2, name=LISTNAME2, **LISTMETA, items=[])),
    ('store_item', dict(list_name=LISTNAME2, permissions=PERMISSIONS, item=ITEM), dict(item_id=4, list_id=2)),
    ('store_item', dict(list_name=LISTNAME3, permissions={}, item=ITEM), dict(success=False)),
    ('store_item', dict(list_name=LISTNAME3, permissions=PERMISSIONS, item=ITEM), dict(item_id=5, list_id=3)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True), [
        dict(id=4, list_id=2, **ITEM),
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('delete_all', dict(list_name=LISTNAME2, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True), [
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False),
     [dict(id=3, name=LISTNAME3, title=None, properties=None)]),
    ('delete_all', dict(list_name=LISTNAME3, permissions=PERMISSIONS), dict(success=True)),
    ('delete_all', dict(list_name=LISTNAME3 + 'x', permissions=PERMISSIONS), dict(success=False)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False), []),
]


models = setup_db('controllers')
controllers = Controllers(models)

for step, (method, kwargs, expected) in enumerate(CONTROLLERS_SCRIPT):
    globals()[f'test_list_manager_controllers_{step:02d}_{method}'] = \
        single_test(controllers, method, kwargs, expected)
