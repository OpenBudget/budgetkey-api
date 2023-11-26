from datetime import datetime

from budgetkey_api.list_manager.models import Models


FAILED = dict(success=False)
SUCCESS = dict(success=True)


class Controllers():

    def __init__(self, models: Models):
        self.models = models

    def _get_or_create_list(self, list_name, user_id):
        list_rec = None
        if list_name:
            list_rec = self.models.get_list(list_name, user_id)
        if not list_rec:
            list_rec = self.models.create_list(list_name, user_id)
        return list_rec

    def store_item(self, permissions, list_name, item):
        user_id = permissions.get("userid")
        if not user_id:
            return FAILED
        list_rec = self._get_or_create_list(list_name, user_id)
        added_item = self.models.add_item(list_rec['id'], item)
        return dict(
            item_id=added_item['id'],
            list_id=list_rec['id'],
            list_name=list_rec['name']
        )

    def store_list(self, permissions, list_name, rec):
        user_id = permissions.get("userid")
        if not user_id:
            return FAILED
        list_rec = self._get_or_create_list(list_name, user_id)
        self.models.update_list(list_rec['id'], rec)
        return dict(
            id=list_rec['id']
        )

    def get_authenticated(self, list_name, user_id, items, kind):
        if list_name:
            list_rec = self.models.get_list(list_name, user_id)
            if not list_rec:
                return FAILED
            if items:
                list_rec['items'] = self.models.get_items(list_name, user_id)
            return self.process_dates(list_rec)
        else:
            if items:
                return self.process_dates(self.models.get_all_items(user_id, kind))
            else:
                return self.process_dates(self.models.get_all_lists(user_id, kind))

    def get_unauthenticated(self, list_name, list_user_id, items):
        if list_name:
            list_rec = self.models.get_list(list_name, list_user_id)
            if not list_rec:
                return FAILED
            if not list_rec['visibility']:
                return FAILED
            if items:
                list_rec['items'] = self.models.get_items(list_name, list_user_id)
            return self.process_dates(list_rec)
        else:
            return FAILED

    def get(self, permissions, list_name, items, kind, list_user_id):
        user_id = permissions.get('userid')
        if list_user_id:
            return self.get_unauthenticated(list_name, list_user_id, items)
        elif user_id:
            return self.get_authenticated(list_name, user_id, items, kind, )
        else:
            return FAILED

    def delete(self, permissions, item_id):
        user_id = permissions.get('userid')
        if not user_id:
            return FAILED
        item_id = int(item_id)
        list_rec = self.models.get_list_by_item(item_id)
        if not list_rec or list_rec['user_id'] != user_id:
            return FAILED
        self.models.delete_item(item_id)
        return SUCCESS

    def delete_all(self, permissions, list_name):
        user_id = permissions.get('userid')
        if not user_id:
            return FAILED
        list_rec = self.models.get_list(list_name, user_id)
        if not list_rec:
            return FAILED
        self.models.delete_list(list_rec['id'])
        return SUCCESS

    def process_dates(self, obj):
        if isinstance(obj, dict):
            return dict(
                (k, self.process_dates(v))
                if k not in ('create_time', 'update_time') or not isinstance(v, datetime)
                else (k, v.isoformat())
                for k, v in obj.items()
            )
        elif isinstance(obj, list):
            return [self.process_dates(item) for item in obj]
        else:
            return obj
