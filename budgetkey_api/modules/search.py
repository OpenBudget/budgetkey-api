import os

import elasticsearch
from openai import OpenAI

from apies import apies_blueprint
from apies.query import Query


from .caching import add_cache_header

DATAPACKAGE_BASE = 'pkg-cache/{}/datapackage.json'
ES_HOST = os.environ.get('ES_HOST', 'localhost')
ES_PORT = int(os.environ.get('ES_PORT', '9200'))
ES_CONNECTION = os.environ.get('ES_CONNECTION')
ES_CERT_PATH = os.environ.get('ES_CERT_PATH')
INDEX_NAME = os.environ.get('INDEX_NAME', 'budgetkey')
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')


def text_rules(field):
    if field.get('es:title'):
        if field.get('es:keyword'):
            return [('exact', '^10')]
        else:
            return [('inexact', '^10'), ('natural', '.hebrew^3')]
    elif field.get('es:hebrew'):
        return [('inexact', ''), ('natural', '.hebrew')]
    elif field.get('es:boost'):
        if field.get('es:keyword'):
            return [('exact', '^10')]
        else:
            return [('inexact', '^10')]
    elif field.get('es:keyword'):
        return [('exact', '')]
    else:
        return [('inexact', '')]


TYPES = [
    'people',
    'tenders',
    'entities',
    'contract-spending',
    'national-budget-changes',
    'supports',
    'reports',
    'budget',
    'gov_decisions',
    'calls_for_bids',
    'support_criteria',
    'activities',
    'muni_budgets',
    'muni_tenders',
]


EXCEPTIONS = {
    # 'contract-spending': '20191226180556919439_33d16b3f',
}
EXCEPTION_TYPES = [
    ('_' + EXCEPTIONS[t]) if t in EXCEPTIONS else ''
    for t in TYPES
]


class BudgetkeyQuery(Query):

    def __init__(self, search_indexes):
        super().__init__(search_indexes)
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None

    def apply_term(self, term, text_fields, multi_match_type='most_fields', multi_match_operator='and'):
        super().apply_term(term, text_fields, multi_match_type, multi_match_operator)
        if term and len(term) >= 5 and self.openai_client:
            embedding = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=term
            )
            embedding = embedding.data[0].embedding
            for type_name in self.types:
                chunks=dict(
                    knn=dict(
                        field="chunks.embeddings",
                        query_vector=embedding,
                        k=10,
                        num_candidates=50,
                        boost=0.5
                    )
                )
                should = self.must(type_name)[-1]
                should['bool']['should'].append(chunks)


def setup_search(app):
    client_params = dict(
        request_timeout=60
    )
    if ES_CONNECTION:
        client_params['hosts'] = ES_CONNECTION
    else:
        client_params['hosts'] = [dict(host=ES_HOST, port=ES_PORT, scheme='http')]
    if ES_CERT_PATH:
        client_params['ca_certs'] = ES_CERT_PATH
    if ELASTIC_PASSWORD:
        client_params['basic_auth'] = ('elastic', ELASTIC_PASSWORD)
    client = elasticsearch.Elasticsearch(**client_params)
    blueprint = apies_blueprint(
        app,
        [
            DATAPACKAGE_BASE.format(doctype)
            for doctype in TYPES
        ],
        client,
        dict(
            (t, f'{INDEX_NAME}__{t}{e}')
            for t, e in zip(TYPES, EXCEPTION_TYPES)
        ),
        f'{INDEX_NAME}__docs',
        dont_highlight={
            'kind',
            'kind_he',
            'tender_type_he',
            'budget_code',
            'entity_kind',
            'entity_id',
            'code',
            'decision',
            'simple_decision',
        },
        multi_match_type='best_fields',
        multi_match_operator='and',
        text_field_rules=text_rules,
        debug_queries=True,
        query_cls=BudgetkeyQuery,
    )
    add_cache_header(blueprint, 600)
    app.register_blueprint(blueprint, url_prefix='/')
    return blueprint
