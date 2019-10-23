from typing import Any


class CStatement:
    def __init__(self, name: str):
        '''
            Any str will be left as is
        '''
        self.name = name

    def __repr__(self) -> str:
        return str(self.name)

    def __and__(self, other):
        return CStatement(f'{self.name} AND {other.name}')

    def __or__(self, other):
        return CStatement(f'{self.name} OR {other.name}')


class Column:
    def __init__(self, name: str, c_type: Any, null: bool = True,
                 default: str = ''):
        self.name = name
        self.c_type = c_type
        self.null = null

    def _check_tp(self, what: Any):
        if self.c_type == str:
            return _escape(what)
        else:
            return str(what)

    def __repr__(self) -> str:
        return str(self.name)

    def __hash__(self) -> str:
        return hash(self.name)

    def __eq__(self, what: Any) -> CStatement:
        return CStatement(f'`{self.name}`={self._check_tp(what)}')

    def __ne__(self, what: Any) -> CStatement:
        return CStatement(f'`{self.name}`!={self._check_tp(what)}')

    def __lt__(self, what: Any) -> CStatement:
        return CStatement(f'`{self.name}`<{self._check_tp(what)}')

    def __gt__(self, what: Any) -> CStatement:
        return CStatement(f'`{self.name}`>{self._check_tp(what)}')

    def __le__(self, what: Any) -> CStatement:
        return CStatement(f'`{self.name}`<={self._check_tp(what)}')

    def __ge__(self, what: Any) -> CStatement:
        return CStatement(f'`{self.name}`>={self._check_tp(what)}')


class Table:
    def __init__(self, t_name: str, *columns: Column):
        self._t_name = t_name
        self.attrs = {}

        for column in columns:
            self.attrs[column.name] = column

    def __getattr__(self, attr: str):
        return self.attrs[attr]

    def __repr__(self) -> str:
        return self._t_name


class Command:
    def __init__(self, name: str, *argv):
        '''
            Set name and argv for SQL function\n
            Like a: Command('concat', 'SQL', 'is', 'cool')\n
            Will be translated to: CONCAT('SQL', 'is', 'cool')
        '''

        self.name = name.upper()+'('
        self.name += ', '.join(map(self._command, argv)) + ')'

    def _command(self, value: Any) -> str:
        if isinstance(value, str):
            return _escape(value)
        else:
            return str(value)

    def __repr__(self) -> str:
        return self.name


class Query:
    def __init__(self, query: str):
        self.query = query

    def __repr__(self) -> str:
        return str(self.query)


class WHERE:
    def __init__(self, *pairs: CStatement):
        pairs = map(str, pairs)

        self.where = 'WHERE '
        self.where += ' AND '.join(pairs)

    def __repr__(self) -> str:
        return str(self.where)


def _escape(value: str) -> str:
    value = value.replace("'", "''")
    return f"'{value}'"


def _prepare_string(pairs: dict) -> list:
    statements = []

    for name, value in pairs.items():
        if not isinstance(name, str):
            if name.c_type == str:
                value = _escape(value)
        else:
            value = _escape(value) if isinstance(value, str) else str(value)

        statements.append(
            f"`{name}`={value}"
        )

    return statements
