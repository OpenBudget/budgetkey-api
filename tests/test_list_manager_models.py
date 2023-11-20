import datetime

from .consts import (
    LISTNAME, LISTNAME2, LISTNAME3, USERID, USERID2, ITEM, ITEMS,
    LISTMETA, LISTNOMETA, LISTKIND, MOCK_UUID, time_checker, setup_db
)


def single_test(obj, method, kwargs, expected):
    now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)

    def func():
        print('Testing', method, kwargs, expected)
        actual = getattr(obj, method)(**kwargs)
        time_checker(now, actual)
        assert actual == expected
    return func


MODEL_OUTITEMS = [
    dict(id=i + 1, list_id=1, **item)
    for i, item in enumerate(ITEMS)
]

MODELS_SCRIPT = [
    ('get_list', dict(list_name=LISTNAME, user_id=USERID), None),
    ('create_list', dict(list_name=LISTNAME, user_id=USERID),
     dict(id=1, name=LISTNAME, user_id=USERID, **LISTNOMETA)),
    ('add_item', dict(list_id=1, item=ITEM), dict(id=1, list_id=1, **ITEM)),
    *[
        ('add_item', dict(list_id=1, item=item), outitem)
        for item, outitem in zip(ITEMS, MODEL_OUTITEMS)
    ],
    ('get_items', dict(list_name=LISTNAME, user_id=USERID), MODEL_OUTITEMS),
    ('delete_item', dict(item_id=2), None),
    ('get_items', dict(list_name=LISTNAME, user_id=USERID), [MODEL_OUTITEMS[0], MODEL_OUTITEMS[2]]),
    ('delete_list', dict(list_id=1), None),
    ('get_items', dict(list_name=LISTNAME, user_id=USERID), []),
    ('create_list', dict(list_name=LISTNAME2, user_id=USERID),
     dict(id=2, name=LISTNAME2, user_id=USERID, **LISTNOMETA)),
    ('create_list', dict(list_name=LISTNAME3, user_id=USERID),
     dict(id=3, name=LISTNAME3, user_id=USERID, **LISTNOMETA)),
    ('update_list', dict(list_id=3, rec=LISTMETA), dict(id=3, name=LISTNAME3, user_id=USERID, **LISTMETA)),
    ('get_all_lists', dict(user_id=USERID), [
        dict(id=2, name=LISTNAME2, **LISTNOMETA),
        dict(id=3, name=LISTNAME3, **LISTMETA),
    ]),
    ('get_all_lists', dict(user_id=USERID2), [
    ]),
    ('get_all_lists', dict(user_id=USERID, kind=LISTKIND), [
        dict(id=3, name=LISTNAME3, **LISTMETA),
    ]),
    ('get_list', dict(list_name=LISTNAME3, user_id=USERID), dict(id=3, name=LISTNAME3, user_id=USERID,  **LISTMETA)),
    ('get_list', dict(list_name=LISTNAME3, user_id=USERID2), None),
    ('get_all_items', dict(user_id=USERID), []),
    ('add_item', dict(list_id=2, item=ITEM), dict(id=4, list_id=2, **ITEM)),
    ('add_item', dict(list_id=3, item=ITEM), dict(id=5, list_id=3, **ITEM)),
    ('get_all_items', dict(user_id=USERID), [dict(id=4, list_id=2, **ITEM), dict(id=5, list_id=3, **ITEM)]),
    ('get_all_items', dict(user_id=USERID, kind=LISTKIND), [dict(id=5, list_id=3, **ITEM)]),
    ('delete_list', dict(list_id=2), None),
    ('get_all_items', dict(user_id=USERID), [dict(id=5, list_id=3, **ITEM)]),
    ('get_all_lists', dict(user_id=USERID), [
        dict(id=3, name=LISTNAME3, **LISTMETA),
    ]),
    ('delete_list', dict(list_id=3), None),
    ('get_all_lists', dict(user_id=USERID), []),
    ('create_list', dict(list_name=None, user_id=USERID, rec=LISTMETA),
     dict(id=4, name=MOCK_UUID, user_id=USERID, **LISTMETA)),
]


models = setup_db('models')

for step, (method, kwargs, expected) in enumerate(MODELS_SCRIPT):
    globals()[f'test_list_manager_models_{step:02d}_{method}'] = single_test(models, method, kwargs, expected)
