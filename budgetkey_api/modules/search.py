import os

import elasticsearch

from apies import apies_blueprint
from apies.query import Query


from .caching import add_cache_header

DATAPACKAGE_BASE = 'pkg-cache/{}/datapackage.json'
ES_HOST = os.environ.get('ES_HOST', 'localhost')
ES_PORT = int(os.environ.get('ES_PORT', '9200'))
INDEX_NAME = os.environ.get('INDEX_NAME', 'budgetkey')


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
    ...


def setup_search(app):
    blueprint = apies_blueprint(
        app,
        [
            DATAPACKAGE_BASE.format(doctype)
            for doctype in TYPES
        ],
        elasticsearch.Elasticsearch([dict(host=ES_HOST, port=ES_PORT)], timeout=60),
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
        debug_queries=False,
        query_cls=BudgetkeyQuery,
    )
    add_cache_header(blueprint, 600)
    app.register_blueprint(blueprint, url_prefix='/')
    return blueprint
