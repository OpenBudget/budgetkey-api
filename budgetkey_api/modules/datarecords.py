import os

import requests

from flask import Blueprint, abort
from flask_jsonpify import jsonpify

from .caching import add_cache_header

DATARECORDS_URL = os.environ.get('DATARECORDS_URL', 'https://data-input.obudget.org/api/datarecords')
TIMEOUT = 24 * 60 * 60  # one day

KEYS = [
    'target_age_group',
    'subject',
    'intervention',
    'target_audience',
]


class DataRecordsBlueprint(Blueprint):

    def __init__(self, cache):
        super().__init__('datarecords', 'datarecords')
        self.cache = cache

        self.add_url_rule(
            '/datarecords/<key>',
            'datarecords',
            self.get_datarecords,
            methods=['GET']
        )

    def fetch_datarecords(self, key):
        response = requests.get(f'{DATARECORDS_URL}/{key}', timeout=60)
        response.raise_for_status()
        return response.json()

    def get_datarecords(self, key):
        if key not in KEYS:
            abort(404, f'Data record {key} not found. Available keys: {", ".join(KEYS)}')
        cache_key = f'datarecords/{key}'
        data = self.cache.get(cache_key)
        if data is None:
            try:
                data = self.fetch_datarecords(key)
            except Exception as e:
                abort(502, f'Failed to fetch data records for {key}: {e}')
            self.cache.set(cache_key, data, timeout=TIMEOUT)
        return jsonpify(data)


def setup_datarecords(app, cache):
    bp = DataRecordsBlueprint(cache)
    add_cache_header(bp, TIMEOUT)
    app.register_blueprint(bp, url_prefix='/api/')
    return bp
