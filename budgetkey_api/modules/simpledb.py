import os
from pathlib import Path
from contextlib import contextmanager

import requests
import json

from flask import Blueprint, abort, current_app, request
from flask_jsonpify import jsonpify

from sqlalchemy import create_engine, text

from .caching import add_cache_header

ROOT_DIR = Path(__file__).parent


class SimpleDBBlueprint(Blueprint):

    TABLES = [
        'budget_items_data',
        'income_items_data',
        # 'budget_topics_data',
        # 'supports_data',
        # 'contracts_data',
        # 'entities_data',
        # 'tenders_data'
    ]

    DATAPACKAGE_URL = 'https://next.obudget.org/datapackages/simpledb'

    def __init__(self, connection_string, search_blueprint):
        super().__init__('simpledb', 'simpledb')
        self.connection_string = connection_string
        self.tables, self.search_params = self.process_tables()
        self.search_blueprint = search_blueprint
        self.add_url_rule(
            '/tables/<table>/info',
            'table-info',
            self.get_table,
            methods=['GET']
        )

        self.add_url_rule(
            '/tables',
            'table-list',
            self.get_tables,
            methods=['GET']
        )

        if search_blueprint:
            self.add_url_rule(
                '/tables/<table>/search',
                'table-search',
                self.simple_search,
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
        sp = dict()
        with self.connect_db() as connection:
            for table in self.TABLES:
                try:
                    rec = {}
                    datapackage_url = f'{self.DATAPACKAGE_URL}/{table}/datapackage.json'
                    package_descriptor = requests.get(datapackage_url).json()
                    description = package_descriptor['resources'][0]['description']
                    fields = package_descriptor['resources'][0]['schema']['fields']
                    rec['description'] = description
                    rec['fields'] = [dict(
                        name=f['name'],
                        **f.get('details', {})
                    ) for f in fields]
                    rec['schema'] = self.get_schema(connection, table)
                    ret[table] = rec
                    sp[table] = package_descriptor['resources'][0]['search']
                except Exception as e:
                    print(f'Error processing table {table}: {e}')
        return ret, sp

    def get_schema(self, connection, table):
        query = text(f"select generate_create_table_statement('{table}')")
        result = connection.execute(query)
        create_table = result.fetchone()[0]
        return create_table

    def get_table(self, table):
        if table not in self.tables:
            abort(404, f'Table {table} not found. Available tables: {", ".join(self.tables.keys())}')
        return jsonpify(self.tables[table])

    def get_tables(self):
        return jsonpify(list(self.tables.keys()))

    def simple_search(self, table):
        params = self.search_params[table]

        q = request.args.get('q', '')
        filters = params.get('filters', {}) or {}
        filters = json.dumps([filters])

        es_client = current_app.config['ES_CLIENT']
        ret = self.search_blueprint.controllers.search(
            es_client, [params['index']], q,
            size=20,
            offset=0,
            filters=filters,
            score_threshold=0,
            highlight=[],
            snippets=[],
            match_operator='or'
        )
        results = []
        search_results = ret.get('search_results')
        for rec in search_results:
            rec = rec.get('source')
            rec = {k1: rec.get(k2) for k1, k2 in params['field_map'].items()}
            results.append(rec)
        ret['search_results'] = results
        return jsonpify(ret)


def setup_simpledb(app, es_blueprint):
    sdb = SimpleDBBlueprint(os.environ['DATABASE_READONLY_URL'], es_blueprint)
    add_cache_header(sdb, 3600)
    app.register_blueprint(sdb, url_prefix='/api/')
