from budgetkey_api.modules.simpledb import check_for_common_errors

MIXED = 'Matching codes with different levels'
LIKE = 'Matching code with wildcard'


def warnings_for(sql, table='budget_items_data'):
    return check_for_common_errors(table, sql)


def has(warnings, prefix):
    return any(w.startswith(prefix) for w in warnings)


def test_mixing_levels_without_level_filter_warns():
    assert has(warnings_for("SELECT SUM(amount_allocated) FROM budget_items_data WHERE code IN ('24', '24.07.14')"),
               MIXED)


def test_mixing_levels_with_level_filter_is_fine():
    sql = ("SELECT SUM(amount_allocated) FROM budget_items_data "
           "WHERE level = 4 AND (LEFT(code, 2) = '34' OR code IN ('38.30.02.24', '38.30.02.01'))")
    assert not has(warnings_for(sql), MIXED)


def test_level_in_filter_is_fine():
    sql = "SELECT code FROM budget_items_data WHERE level IN (3, 4) AND code IN ('24.07', '24.07.14')"
    assert not has(warnings_for(sql), MIXED)


def test_bare_numbers_are_not_codes():
    # LIMIT 10 and LEFT(code, 10) used to be read as a level-1 code next to the level-4 one.
    sql = ("SELECT title, item_url FROM budget_items_data WHERE year = 2026 AND code = '34.30.03.44' "
           "ORDER BY LEFT(code, 10) LIMIT 10")
    assert warnings_for(sql) == []


def test_same_level_codes_are_fine():
    assert warnings_for("SELECT * FROM budget_items_data WHERE code IN ('24.07.14', '93.01.01')") == []


def test_like_without_level_filter_warns():
    assert has(warnings_for("SELECT SUM(amount_allocated) FROM budget_items_data WHERE code LIKE '24%'"), LIKE)


def test_like_with_level_filter_is_fine():
    assert not has(warnings_for("SELECT SUM(amount_allocated) FROM budget_items_data "
                                "WHERE code LIKE '24%' AND level = 2"), LIKE)


def test_other_tables_are_not_checked():
    assert warnings_for("SELECT * FROM contracts_data WHERE budget_code IN ('24', '24.07.14')",
                        table='contracts_data') == []
