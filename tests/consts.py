import os
import dotenv
import datetime

dotenv.load_dotenv('tests/sample.env')

LISTNAME = 'saved-searches'
LISTNAME2 = 'my-second-list'
LISTNAME3 = 'my-third-list'
LISTPROPS = {'author': 'me', 'tags': ['a', 'b']}
LISTTITLE = 'My List'
LISTKIND = 'my-kind'
LISTKIND2 = 'my-kind2'
LISTMETA = {'title': LISTTITLE, 'properties': LISTPROPS, 'kind': LISTKIND, 'visibility': 1}
LISTMETA_V3 = {**LISTMETA, 'visibility': 3}
LISTNOMETA = {'title': None, 'properties': None, 'kind': None, 'visibility': 0}
USERID = 'user-id-123'
USERID2 = 'user-id-456'
ITEM = {"title": "item1", "url": "http://example.com/1", "properties": {"a": 1, "b": [2, 1]}}
ITEMS = [
    {"title": "item1", "url": "http://example.com/1", "properties": {"a": 1, "b": [1, 2]}},
    {"title": "item2", "url": "http://example.com/2", "properties": {"a": 2, "b": [3, 4]}},
    {"title": "item3", "url": "http://example.com/3", "properties": {"a": 3, "b": [5, 6]}}
]
CONTROLLERS_OUTITEMS = [
    dict(id=i + 1, list_id=1, **item)
    for i, item in enumerate(ITEMS)
]
MOCK_UUID = '7fc2a2e8514746fb9c9a2c6bb02b611e'


def mock_uuid(models):
    models.get_uuid = lambda: MOCK_UUID


def setup_db(key, env=False):
    filename = f'tests/temp/test_list_manager_{key}.sqlite3'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        os.unlink(filename)
    connection_string = f'sqlite:///{filename}'
    if env:
        os.environ['DATABASE_PRIVATE_URL'] = connection_string
    else:
        from budgetkey_api.list_manager import models
        mock_uuid(models)
        return models.Models(connection_string)


def time_checker(now, obj):
    if isinstance(obj, dict):
        create_time = obj.pop('create_time', None)
        if isinstance(create_time, str):
            create_time = datetime.datetime.fromisoformat(create_time)
        assert create_time is None or (create_time - now).seconds <= 5
        update_time = obj.pop('update_time', None)
        if isinstance(update_time, str):
            update_time = datetime.datetime.fromisoformat(update_time)
        assert update_time is None or (update_time - now).seconds <= 5 and update_time >= create_time
        for item in obj.values():
            time_checker(now, item)
    elif isinstance(obj, list):
        for item in obj:
            time_checker(now, item)
