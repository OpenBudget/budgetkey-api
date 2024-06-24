import os
from pathlib import Path
from contextlib import contextmanager

import requests

from flask import Blueprint, abort
from flask_jsonpify import jsonpify

from sqlalchemy import create_engine, text

from .caching import add_cache_header

ROOT_DIR = Path(__file__).parent


class SimpleDBBlueprint(Blueprint):

    TABLES = [
        'budget_items_data',
        'budget_topics_data',
        'supports_data',
        'contracts_data',
        'entities_data',
        'tenders_data'
    ]

    DATAPACKAGE_URL = 'https://next.obudget.org/datapackages/simpledb'

    def __init__(self, connection_string):
        super().__init__('simpledb', 'simpledb')
        self.connection_string = connection_string
        self.tables = self.process_tables()
        self.add_url_rule(
            '/tables/<table>',
            'table',
            self.get_table,
            methods=['GET']
        )

        self.add_url_rule(
            '/tables',
            'tables',
            self.get_tables,
            methods=['GET']
        )

    @contextmanager
    def connect_db(self):
        engine = create_engine(self.connection_string)
        connection = engine.connect()
        try:
            yield connection
        finally:
            connection.close()
            engine.dispose()
            del engine

    def process_tables(self):
        ret = dict()
        with self.connect_db() as connection:
            for table in self.TABLES:
                rec = ret.setdefault(table, dict())
                datapackage_url = f'{self.DATAPACKAGE_URL}/{table}/datapackage.json'
                package_descriptor = requests.get(datapackage_url).json()
                details = package_descriptor['resources'][0]['details']
                fields = package_descriptor['resources'][0]['schema']['fields']
                rec['details'] = details
                rec['fields'] = [dict(
                    name=f['name'],
                    **f.get('details', {})
                ) for f in fields]
                rec['schema'] = self.get_schema(connection, table)
        return ret

    def get_schema(self, connection, table):
        query = text(f"select generate_create_table_statement('{table}')")
        result = connection.execute(query)
        create_table = result.fetchone()[0]
        return create_table

    def get_table(self, table):
        if table not in self.tables:
            abort(404)
        return jsonpify(self.tables[table])

    def get_tables(self):
        return jsonpify(list(self.tables.keys()))


def setup_simpledb(app):
    sdb = SimpleDBBlueprint(os.environ['DATABASE_READONLY_URL'])
    add_cache_header(sdb, 3600)
    app.register_blueprint(sdb, url_prefix='/api/')
