import json

from .models import (
    get_list, add_item, create_list, get_items,
    delete_item, delete_list, get_list_by_item
)


def store(permissions, list_name, item):
    user_id = permissions.get("userid")
    if not user_id:
        return False
    list_rec = get_list(list_name, user_id)
    if not list_rec:
        list_rec = create_list(list_name, user_id)
    item['properties'] = json.dumps(item.get('properties'))
    added_item = add_item(list_name, user_id, item)
    return dict(
        item_id=added_item['id'],
        list_id=list_rec['id']
    )


def get(permissions, list_name):
    user_id = permissions.get('userid')
    if not user_id:
        return False
    list_rec = get_list(list_name, user_id)
    if not list_rec:
        return False
    return {'id': list_rec['id'], 'items': get_items(list_name, user_id)}


def delete(permissions, item_id):
    user_id = permissions.get('userid')
    if not user_id:
        return False
    item_id = int(item_id)
    list_rec = get_list_by_item(item_id)
    if not list_rec or list_rec['user_id'] != user_id:
        return False
    delete_item(item_id)
    return True


def delete_all(permissions, list_name):
    user_id = permissions.get('userid')
    if not user_id:
        return False
    list_rec = get_list(list_name, user_id)
    if not list_rec:
        return False
    delete_list(list_rec['id'])
    return True
