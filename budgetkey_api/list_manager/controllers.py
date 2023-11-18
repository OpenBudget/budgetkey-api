FAILED = dict(success=False)
SUCCESS = dict(success=True)


class Controllers():

    def __init__(self, models):
        self.models = models

    def store(self, permissions, list_name, item):
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

    def get(self, permissions, list_name, items):
        user_id = permissions.get('userid')
        if not user_id:
            return FAILED
        if list_name:
            list_rec = self.models.get_list(list_name, user_id)
            if not list_rec:
                return FAILED
            return {'id': list_rec['id'], 'items': self.models.get_items(list_name, user_id)}
        else:
            if items:
                return self.models.get_all_items(user_id)
            else:
                return self.models.get_all_lists(user_id)

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
