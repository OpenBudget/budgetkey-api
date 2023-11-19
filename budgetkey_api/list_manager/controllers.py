FAILED = dict(success=False)
SUCCESS = dict(success=True)


class Controllers():

    def __init__(self, models):
        self.models = models

    def store_item(self, permissions, list_name, item):
        user_id = permissions.get("userid")
        if not user_id:
            return FAILED
        list_rec = self.models.get_list(list_name, user_id)
        if not list_rec:
            list_rec = self.models.create_list(list_name, user_id)
        added_item = self.models.add_item(list_name, user_id, item)
        return dict(
            item_id=added_item['id'],
            list_id=list_rec['id']
        )

    def store_list(self, permissions, list_name, rec):
        user_id = permissions.get("userid")
        if not user_id:
            return FAILED
        list_rec = self.models.get_list(list_name, user_id)
        if not list_rec:
            list_rec = self.models.create_list(list_name, user_id)
        self.models.update_list(list_rec['id'], rec)
        return dict(
            id=list_rec['id']
        )

    def get(self, permissions, list_name, items):
        user_id = permissions.get('userid')
        if not user_id:
            return FAILED
        if list_name:
            list_rec = self.models.get_list(list_name, user_id)
            if not list_rec:
                return FAILED
            list_rec.pop('user_id')
            if items:
                list_rec['items'] = self.models.get_items(list_name, user_id)
            ret = self.process_dates(list_rec)
            print('ITEMS', ret, list_name, items)
            return self.process_dates(list_rec)
        else:
            if items:
                return self.process_dates(self.models.get_all_items(user_id))
            else:
                return self.process_dates(self.models.get_all_lists(user_id))

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
                if k not in ('create_time', 'update_time')
                else (k, v.isoformat())
                for k, v in obj.items()
            )
        elif isinstance(obj, list):
            return [self.process_dates(item) for item in obj]
        else:
            return obj
