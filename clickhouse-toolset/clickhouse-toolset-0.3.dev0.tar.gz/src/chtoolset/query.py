from chtoolset._query import _replace_tables, format, tables, table_if_is_simple_query
from collections import defaultdict
from toposort import toposort

def tables_or_sql(sql):
    try:
        return set(tables(sql))
    except:
        return set([('', sql)])

class ReplacementsDict(dict):
    def __getitem__(self, key):
        v = super().__getitem__(key)
        return v() if callable(v) else v

def replace_tables(sql, replacements):
    if not replacements:
        return format(sql)

    _replacements = ReplacementsDict()
    for k, r in replacements.items():
        rk = k if isinstance(k, tuple) else ('', k)
        _replacements[rk] = r

    deps = defaultdict(set)
    _tables = tables(sql)
    seen_tables = set()
    while _tables:
        table = _tables.pop()
        seen_tables.add(table)
        if table in _replacements:
            replacement = _replacements[table]
            dependent_tables = tables_or_sql(replacement)
            deps[table] |= dependent_tables
            for dependent_table in list(dependent_tables):
                if dependent_table not in seen_tables:
                    _tables.append(dependent_table)
    deps_sorted = list(reversed(list(toposort(deps))))

    if not deps_sorted:
        return format(sql)

    for current_deps in deps_sorted:
        current_replacements = {}
        for r in current_deps:
            if r in _replacements:
                replacement = _replacements[r]
                simplified_replacement = table_if_is_simple_query(replacement)
                if simplified_replacement and not simplified_replacement[0]:  # Do not simplify if the database is set, e.g. (public, taxi) as we want to keep the database.
                    replacement = simplified_replacement[1]
                current_replacements[r] = replacement
        sql = _replace_tables(sql, current_replacements)
    return sql
