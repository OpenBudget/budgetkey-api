import os
import re
from pathlib import Path
from contextlib import contextmanager
import datetime

import requests
import json
from hashlib import md5

from flask import Blueprint, abort, current_app, request, Response
from flask_jsonpify import jsonpify

from sqlalchemy import create_engine, text

from .caching import add_cache_header

ROOT_DIR = Path(__file__).parent


def check_for_common_errors(table, sql):
    ret = []
    if table == 'budget_items_data':
        likes = re.search(r'''code like .([\d\.]+)%''', sql, re.I | re.M | re.S | re.U)
        if likes:
            code = likes.group(1)
            code_parts = code.split('.')
            ret.append(
                'Matching code with wildcard "%" is usually a mistake, as it fetches codes from different '
                'budget levels. If you are aggregating budget amount, such a query would summarize a top '
                'level item with all of its children, which would be counting the same item multiple times. '
                f"Use an exact match instead, e.g. `code = '{code}'` or filter the query using the `level` field "
                f'(in your case, `level={len(code_parts)}`).'
            )
        codes = re.findall(r'[^\d\.](\d\d(\.\d\d){0,3})[^\d\.]', sql, re.I | re.M | re.S | re.U)
        codes = [c[0] for c in codes]
        code_lengths = set(len(c) for c in codes)
        if len(code_lengths) > 1:
            ret.append(
                'Matching codes with different levels is usually a mistake. If you are aggregating budget amount, '
                'such a query would summarize a top level item on of its children, which would be counting the same '
                'item multiple times. Use an exact match instead, e.g. "code = 12.34.56" or filter the query using the '
                '`level` field.'
            )
    group_by_item_url = re.search(r'group by.+item_url', sql, re.I | re.M | re.S | re.U)
    if group_by_item_url:
        ret.append(
            'Using "GROUP BY" with "item_url" may lead to unwanted results.'
            'If you are aggregating multiple items, remove the "item_url" from the query '
            'or use "ARRAY_AGG(item_url)"'
        )
    return ret


class TableHolder:

    TABLES = [
        'budget_items_data',
        'income_items_data',
        # 'budget_topics_data',
        'supports_data',
        'contracts_data',
        'entities_data',
        # 'tenders_data',
        'budgetary_change_requests_data',
        'budgetary_change_transactions_data',
    ]

    DATAPACKAGE_URL = 'https://next.obudget.org/datapackages/simpledb'
    TIMEOUT = 600

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.infos = dict()
        self.schemas = dict()

    def get_info(self, table):
        info, _ = self.get_table_data(table)
        if info:
            info['schema'] = self.get_schema(table)
        return info

    def get_schema(self, table):
        if not self.schemas.get(table):
            self.schemas[table] = self.get_schema_from_db(table)
        return self.schemas[table]

    def get_search_params(self, table):
        _, search = self.get_table_data(table)
        return search

    def get_table_data(self, table):
        fetch = True
        current_hash = None
        if table in self.infos:
            info, search, ts, current_hash = self.infos[table]
            if (datetime.datetime.now() - ts).seconds < self.TIMEOUT:
                fetch = False
        if fetch:
            info, search, hash = self.fetch_table(table)
            if info is not None:
                self.infos[table] = (info, search, datetime.datetime.now(), hash)
                if current_hash != hash:
                    self.schemas[table] = None
        if table not in self.infos:
            return None, None
        info, search, _, _ = self.infos[table]
        return info, search

    def get_schema_from_db(self, table):
        with self.connect_db() as connection:
            query = text(f"select generate_create_table_statement('{table}')")
            result = connection.execute(query)
            create_table = result.fetchone()[0]
            return create_table

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

    def fetch_table(self, table):
        if table in self.TABLES:
            try:
                rec = {}
                datapackage_url = f'{self.DATAPACKAGE_URL}/{table}/datapackage.json'
                response = requests.get(datapackage_url)
                hash = md5(response.content).hexdigest()
                package_descriptor = response.json()
                description = package_descriptor['resources'][0]['description']
                fields = package_descriptor['resources'][0]['schema']['fields']
                rec['description'] = description
                rec['fields'] = [dict(
                    name=f['name'],
                    **f.get('details', {})
                ) for f in fields]
                return rec, package_descriptor['resources'][0]['search'], hash
            except Exception as e:
                print(f'Error processing table {table}: {e}')
        return None, None, None


class SimpleDBBlueprint(Blueprint):

    MAX_PAYLOAD_SIZE = 120 * 1024  # 120 KB

    def __init__(self, connection_string, search_blueprint, db_blueprint):
        super().__init__('simpledb', 'simpledb')
        self.tables = TableHolder(connection_string)

        self.search_blueprint = search_blueprint
        self.db_blueprint = db_blueprint

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

        if db_blueprint:
            self.add_url_rule(
                '/tables/<table>/query',
                'table-query',
                self.query_table,
                methods=['GET']
            )

    def get_table(self, table):
        ret = self.tables.get_info(table)
        if ret is None:
            abort(404, f'Table {table} not found. Available tables: {", ".join(self.tables.TABLES)}')
        return jsonpify(ret)

    def get_tables(self):
        return jsonpify(self.tables.TABLES)

    def trim_json(self, data, rows_field, count_field, max_size):
        rows = data.get(rows_field, [])
        data[rows_field] = []
        ret_json = json.dumps(data, ensure_ascii=False)
        current_len = len(ret_json)
        trimmed_rows = []
        for row in rows:
            row_json = json.dumps(row, ensure_ascii=False)
            current_len += len(row_json) + 2
            if current_len > max_size:
                break
            else:
                trimmed_rows.append(row)
        data[count_field] = len(trimmed_rows)
        data[rows_field] = trimmed_rows
        ret_json = json.dumps(data, ensure_ascii=False)
        return ret_json

    def query_table(self, table):
        ret = self.tables.get_info(table)
        if ret is None:
            abort(404, f'Table {table} not found. Available tables: {", ".join(self.tables.TABLES)}')

        sql = request.args.get('query')
        if sql is None:
            abort(400, 'Missing query parameter')
        num_rows = request.args.get('page_size', 100) or 100
        num_rows = int(num_rows)
        ret = self.db_blueprint.controllers.query_db(sql, num_rows=num_rows, page_size=num_rows, page=0)
        if 'download_url' in ret and self.db_blueprint.external_url:
            ret['download_url'] = self.db_blueprint.external_url + ret['download_url']
        warnings = check_for_common_errors(table, sql)
        if warnings:
            ret['warnings'] = warnings
        ret = dict(
            download_url=ret.get('download_url'),
            warnings=ret.get('warnings'),
            num_rows=ret.get('page_size', 0),
            total_rows=ret.get('total', 0),
            rows=ret.get('rows', []),
        )
        ret = self.trim_json(ret, 'rows', 'num_rows', self.MAX_PAYLOAD_SIZE)
        return Response(ret, mimetype='application/json')

    def simple_search(self, table):
        params = self.tables.get_search_params(table)
        if params is None:
            abort(404, f'Table {table} not found. Available tables: {", ".join(self.tables.TABLES)}')
        if not isinstance(params, dict):
            ret = dict(
                error=f'Search not available for table "{table}", use DB query instead'
            )
            return jsonpify(ret)

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
            src = rec.get('source')
            res = {}
            for k1, k2 in params['field_map'].items():
                if isinstance(k2, str):
                    k2 = [k2]
                for k in k2:
                    if k in src and src[k] is not None:
                        res[k1] = src[k]
                        break
            results.append(res)
        ret = dict(
            search_results=results,
            num_results=len(results),
            total_results=ret.get('search_counts', {}).get('_current', {}).get('total_overall', 0),
        )
        ret = self.trim_json(ret, 'search_results', 'num_results', self.MAX_PAYLOAD_SIZE)
        return Response(ret, mimetype='application/json')


def setup_simpledb(app, es_blueprint, db_blueprint):
    sdb = SimpleDBBlueprint(os.environ['DATABASE_READONLY_URL'], es_blueprint, db_blueprint)
    add_cache_header(sdb, TableHolder.TIMEOUT)
    app.register_blueprint(sdb, url_prefix='/api/')
