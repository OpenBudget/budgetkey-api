import datetime

from budgetkey_api.list_manager.controllers import Controllers
from .consts import (
    LISTNAME, LISTNAME2, LISTNAME3, USERID, USERID2, ITEM, ITEMS, LISTMETA, LISTNOMETA,
    LISTMETA_V3, LISTKIND, CONTROLLERS_OUTITEMS, MOCK_UUID, time_checker, setup_db
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
PERMISSIONS2 = dict(userid=USERID2)
CONTROLLERS_SCRIPT = [
    ('store_item', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=ITEM),
     dict(id=1, list_id=1, list_name=LISTNAME, **ITEM)),
    *[
        ('store_item', dict(list_name=LISTNAME, permissions=PERMISSIONS, item=item),
         dict(id=i + 1, list_id=1, list_name=LISTNAME, **item))
        for i, item in enumerate(ITEMS)
    ],
    (
        'get', dict(list_name=LISTNAME, permissions={}, items=False, kind=None, list_user_id=None),
        dict(success=False, name=LISTNAME, user_id=None)
    ),
    ('get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=True, kind=None, list_user_id=None),
     dict(id=1, name=LISTNAME, items=CONTROLLERS_OUTITEMS, **LISTNOMETA, user_id=USERID)),
    ('delete', dict(item_id=2, permissions={}), dict(success=False)),
    ('delete', dict(item_id=2, permissions=PERMISSIONS), dict(success=True)),
    ('delete', dict(item_id=212, permissions=PERMISSIONS), dict(success=False)),
    (
        'get', dict(list_name=LISTNAME, permissions=PERMISSIONS, items=True, kind=None, list_user_id=None),
        dict(id=1, name=LISTNAME, items=[
            CONTROLLERS_OUTITEMS[0], CONTROLLERS_OUTITEMS[2]
        ], **LISTNOMETA, user_id=USERID)
    ),
    ('delete_all', dict(list_name=LISTNAME, permissions={}), dict(success=False, name=LISTNAME, user_id=None)),
    ('delete_all', dict(list_name=LISTNAME, permissions=PERMISSIONS), dict(success=True)),
    (
        'get',
        dict(list_name=LISTNAME, permissions=PERMISSIONS, items=False, kind=None, list_user_id=None),
        dict(success=False, name=LISTNAME, user_id=USERID)
    ),
    (
        'store_list', dict(list_name=LISTNAME2, permissions=PERMISSIONS, rec=LISTMETA),
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA)
    ),
    (
        'store_list', dict(list_name=LISTNAME2, permissions={}, rec=LISTMETA),
        dict(success=False, name=LISTNAME2, user_id=None)
    ),
    ('get', dict(list_name=LISTNAME2, permissions=PERMISSIONS, items=False, kind=None, list_user_id=None),
     dict(id=2, name=LISTNAME2, **LISTMETA, user_id=USERID)),
    ('get', dict(list_name=LISTNAME2, permissions=PERMISSIONS, items=True, kind=None, list_user_id=None),
     dict(id=2, name=LISTNAME2, **LISTMETA, items=[], user_id=USERID)),
    ('store_item', dict(list_name=LISTNAME2, permissions=PERMISSIONS, item=ITEM),
     dict(id=4, list_id=2, list_name=LISTNAME2, **ITEM)),
    (
        'store_item', dict(list_name=LISTNAME3, permissions={}, item=ITEM),
        dict(success=False, name=LISTNAME3, user_id=None)
    ),
    ('store_item', dict(list_name=LISTNAME3, permissions=PERMISSIONS, item=ITEM),
     dict(id=5, list_id=3, list_name=LISTNAME3, **ITEM)),

    ('get', dict(list_name=LISTNAME2, permissions={}, items=False, kind=None, list_user_id=USERID),
     dict(id=2, name=LISTNAME2, **LISTMETA, user_id=USERID)),
    ('get', dict(list_name=LISTNAME2, permissions={}, items=True, kind=None, list_user_id=USERID),
     dict(id=2, name=LISTNAME2, **LISTMETA, items=[
         dict(id=4, list_id=2, **ITEM)
     ], user_id=USERID)),
    (
        'get', dict(list_name=LISTNAME3, permissions={}, items=False, kind=None, list_user_id=USERID),
        dict(success=False, name=LISTNAME3, user_id=USERID)
    ),
    (
        'get', dict(list_name=LISTNAME3, permissions={}, items=True, kind=None, list_user_id=USERID),
        dict(success=False, name=LISTNAME3, user_id=USERID)
    ),
    (
        'get', dict(list_name=None, permissions={}, items=False, kind=None, list_user_id=USERID),
        dict(success=False, name=None, user_id=USERID)
    ),
    (
        'get', dict(list_name=None, permissions={}, items=True, kind=None, list_user_id=USERID),
        dict(success=False, name=None, user_id=USERID)
    ),
    (
        'get', dict(list_name='None', permissions={}, items=False, kind=None, list_user_id=USERID),
        dict(success=False, name='None', user_id=USERID)
    ),
    (
        'get', dict(list_name='None', permissions={}, items=True, kind=None, list_user_id=USERID),
        dict(success=False, name='None', user_id=USERID)
    ),
    (
        'get', dict(list_name=None, permissions=PERMISSIONS2, items=False, kind=None, list_user_id=USERID),
        dict(success=False, name=None, user_id=USERID)
    ),
    (
        'get', dict(list_name=None, permissions=PERMISSIONS2, items=True, kind=None, list_user_id=USERID),
        dict(success=False, name=None, user_id=USERID)
    ),

    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True, kind=None, list_user_id=None), [
        dict(id=4, list_id=2, **ITEM),
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True, kind=LISTKIND, list_user_id=None), [
        dict(id=4, list_id=2, **ITEM),
    ]),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False, kind=None, list_user_id=None), [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA),
        dict(id=3, name=LISTNAME3, user_id=USERID, **LISTNOMETA)
    ]),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False, kind=LISTKIND, list_user_id=None), [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA),
    ]),

    ('get', dict(list_name=None, permissions=PERMISSIONS2, items=False, kind=LISTKIND, list_user_id=USERID), [
    ]),
    ('get', dict(list_name=None, permissions={}, items=False, kind=LISTKIND, list_user_id=USERID), [
    ]),
    (
        'store_list', dict(list_name=LISTNAME2, permissions=PERMISSIONS, rec=LISTMETA_V3),
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA_V3)
    ),
    ('get', dict(list_name=None, permissions=PERMISSIONS2, items=False, kind=LISTKIND, list_user_id=USERID), [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA_V3),
    ]),
    ('get', dict(list_name=None, permissions={}, items=False, kind=LISTKIND, list_user_id=USERID), [
        dict(id=2, name=LISTNAME2, user_id=USERID, **LISTMETA_V3),
    ]),
    ('delete_all', dict(list_name=LISTNAME2, permissions=PERMISSIONS), dict(success=True)),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=True, kind=None, list_user_id=None), [
        dict(id=5, list_id=3, **ITEM),
    ]),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False, kind=None, list_user_id=None),
     [dict(id=3, name=LISTNAME3, user_id=USERID, **LISTNOMETA)]),
    ('delete_all', dict(list_name=LISTNAME3, permissions=PERMISSIONS), dict(success=True)),
    (
        'delete_all', dict(list_name=LISTNAME3 + 'x', permissions=PERMISSIONS),
        dict(success=False, name=LISTNAME3 + 'x', user_id=USERID)
    ),
    ('get', dict(list_name=None, permissions=PERMISSIONS, items=False, kind=None, list_user_id=None), []),
    (
        'store_item', dict(list_name=None, permissions=PERMISSIONS, item=ITEM),
        dict(id=6, list_id=4, list_name=MOCK_UUID, **ITEM)
    ),
]


models = setup_db('controllers')
controllers = Controllers(models)

for step, (method, kwargs, expected) in enumerate(CONTROLLERS_SCRIPT):
    globals()[f'test_list_manager_controllers_{step:02d}_{method}'] = \
        single_test(controllers, method, kwargs, expected)
