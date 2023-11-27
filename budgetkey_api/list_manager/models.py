import json

from contextlib import contextmanager

from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from sqlalchemy import Column, Unicode, String, create_engine, Integer, TIMESTAMP
from sqlalchemy.orm import sessionmaker

import uuid

# ## SQL DB
Base = declarative_base()


def get_uuid():
    return uuid.uuid4().hex


def object_as_dict(obj):
    if obj is None:
        return None
    ret = {c.key: getattr(obj, c.key)
           for c in inspect(obj).mapper.column_attrs}
    if isinstance(ret.get('properties'), str):
        ret['properties'] = json.loads(ret['properties'])
    return ret


class List(Base):
    __tablename__ = 'lists'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True,)
    name = Column(Unicode)
    user_id = Column(String(128))
    kind = Column(String(16))
    visibility = Column(Integer, default=0)
    title = Column(Unicode)
    properties = Column(Unicode)
    create_time = Column(TIMESTAMP, server_default=func.now())
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    list_id = Column(Integer)
    url = Column(String(512))
    title = Column(Unicode)
    properties = Column(Unicode)
    create_time = Column(TIMESTAMP, server_default=func.now())
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


class Models():

    def __init__(self, connection_string):
        assert connection_string, \
            "No database defined, please set your DATABASE_PRIVATE_URL environment variable"
        self._sql_engine = create_engine(connection_string)
        self._sql_session = None
        Base.metadata.create_all(self._sql_engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        if self._sql_session is None:
            assert self._sql_engine is not None, \
                "No database defined, please set your DATABASE_URL environment variable"
            self._sql_session = sessionmaker(bind=self._sql_engine)
        session = self._sql_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.expunge_all()

    def get_list(self, list_name, user_id):
        with self.session_scope() as session:
            ret = session.query(List).filter_by(name=list_name, user_id=user_id).first()
            return object_as_dict(ret)

    def get_list_by_item(self, item_id):
        with self.session_scope() as session:
            item = session.get(Item, item_id)
            ret = None
            if item:
                ret = session.get(List, item.list_id)
            return object_as_dict(ret)

    def modify_list_from_rec(self, list_rec, rec):
        rec = rec or {}
        title = rec.get('title')
        properties = rec.get('properties')
        kind = rec.get('kind')
        visibility = rec.get('visibility') or 0
        if not isinstance(properties, str):
            properties = json.dumps(properties)
        list_rec.title = title
        list_rec.properties = properties
        list_rec.kind = kind
        list_rec.visibility = visibility

    def create_list(self, list_name, user_id, rec=None):
        with self.session_scope() as session:
            if not list_name:
                list_name = get_uuid()
            to_add = List(name=list_name, user_id=user_id)
            self.modify_list_from_rec(to_add, rec)
            session.add(to_add)
            session.flush()
            return object_as_dict(to_add)

    def update_list(self, list_id, rec):
        with self.session_scope() as session:
            list_rec = session.get(List, list_id)
            if list_rec:
                self.modify_list_from_rec(list_rec, rec)
                session.add(list_rec)
                return object_as_dict(list_rec)

    def add_item(self, list_id, item):
        with self.session_scope() as session:
            url = item.get('url')
            title = item.get('title')
            properties = item.get('properties')
            assert url and title and isinstance(url, str) and isinstance(title, str)
            if not isinstance(properties, str):
                properties = json.dumps(properties)

            existing_item = session\
                .query(Item)\
                .filter_by(list_id=list_id,
                           title=title,
                           url=url)\
                .first()

            if existing_item is None:
                to_add = Item(list_id=list_id, url=url, title=title, properties=properties)
                session.add(to_add)
                ret = to_add
            else:
                existing_item.properties = properties
                session.add(existing_item)
                ret = existing_item
            session.flush()
            return object_as_dict(ret)

    def get_items(self, list_name, user_id):
        with self.session_scope() as session:
            list_id = session.query(List).filter_by(name=list_name, user_id=user_id).first()
            if not list_id:
                return []
            list_id = list_id.id
            return list(map(object_as_dict,
                            session.query(Item).filter_by(list_id=list_id).order_by(Item.create_time)))

    def get_all_items(self, user_id, kind=None):
        with self.session_scope() as session:
            lists = session.query(List).filter_by(user_id=user_id)
            if kind:
                lists = lists.filter_by(kind=kind)
            list_ids = [lst.id for lst in lists]
            return list(map(object_as_dict,
                            session.query(Item).filter(Item.list_id.in_(list_ids)).order_by(Item.create_time)))

    def get_all_lists(self, user_id, kind=None):
        with self.session_scope() as session:
            ret = session.query(List).filter_by(user_id=user_id)
            if kind:
                ret = ret.filter_by(kind=kind)
            ret = [
                object_as_dict(rec) for rec in ret
            ] if ret else None
            return ret

    def delete_item(self, item_id):
        with self.session_scope() as session:
            item_id = int(item_id)
            session.query(Item).filter_by(id=item_id).delete()

    def delete_list(self, list_id):
        with self.session_scope() as session:
            session.query(Item).filter_by(list_id=list_id).delete()
            session.query(List).filter_by(id=list_id).delete()
