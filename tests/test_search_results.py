from budgetkey_api.modules.search import BudgetkeyQuery


def test_search_results_drop_item_page_fields():
    q = BudgetkeyQuery.__new__(BudgetkeyQuery)  # process_extra needs no ES setup
    results = dict(search_results=[
        dict(type='state_comptroller_audits', source=dict(
            title='t', summary='s', n_findings=3, text='x' * 300000, findings=[{}], findings_text='f',
            earlier_reports=[], key_figures=[], related_items=[{}], mentioned_in=[{}], chunks=[{}])),
        dict(type='gov_decisions', source=dict(title='t', text='decision text', related_items=[{}], chunks=[{}])),
    ])
    q.process_extra(results, None)
    audit, decision = (r['source'] for r in results['search_results'])
    assert audit == dict(title='t', summary='s', n_findings=3)
    assert decision == dict(title='t', text='decision text')  # other types' cards still read text
