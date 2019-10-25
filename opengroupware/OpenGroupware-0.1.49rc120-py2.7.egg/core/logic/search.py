#
# Copyright (c) 2009, 2012, 2013, 2014, 2015, 2016
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from sqlalchemy.sql.expression import desc, asc
from datetime import datetime
from dateutil.tz import gettz
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from coils.core import \
    PropertyManager, \
    Command, \
    CoilsException
from coils.foundation import \
    ObjectProperty, \
    CompanyValue, \
    Address, \
    Telephone, \
    Parse_Value_To_UTCDateTime
from get import \
    RETRIEVAL_MODE_SINGLE, \
    RETRIEVAL_MODE_MULTIPLE
from keymap import \
    COILS_ADDRESS_KEYMAP, \
    COILS_TELEPHONE_KEYMAP, \
    COILS_COMPANYVALUE_KEYMAP


def is_scalar(value, allow_null=True):
    '''
    Return True if a value is scalar, otherwise return False.
    '''
    if not allow_null and value is None:
        return False
    return isinstance(
        value,
        (type(None), unicode, str, int,
         float, bool, datetime, ),
    )


class SearchCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self.mode = RETRIEVAL_MODE_MULTIPLE

    def prepare(self, ctx, **params):
        self._result = []
        self._pr = []
        self._cv = {}
        self._revolve = False
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self._limit = params.get('limit', None)
        if (self._limit is None):
            self._limit = 150
        else:
            self._limit = int(self._limit)
        if ('criteria' in params):
            x = params['criteria']
            if (isinstance(x, dict)):
                x = [x, ]
            self._criteria = x
        else:
            raise CoilsException('Search requested with no criteria.')

        """result revolving"""
        if (str(params.get('revolve', 'NO')).upper() in ['YES', 'TRUE']):
            self._revolve = True

        """sort criteria, if any"""
        self._sort_keys = list()
        if 'sort_keys' in params:
            if isinstance(params.get('sort_keys'), basestring):
                self._sort_keys = params.get('sort_keys').split(',')
            elif isinstance(params.get('sort_keys'), list):
                for sort_key in params.get('sort_keys'):
                    if isinstance(sort_key, basestring):
                        self._sort_keys.append(sort_key)

        self._reverse_sort = False
        if 'reverse_sort' in params:
            if isinstance(params.get('reverse_sort'), basestring):
                if params.get('reverse_sort').upper() == 'YES':
                    self._reverse_sort = True
            else:
                self._reverse_sort = bool(params.get('reverse_sort'))

    def _transform_value(self, value, kind, enumeration):

        if enumeration:
            return [
                self._transform_value(
                    value=x,
                    kind=kind,
                    enumeration=False,
                )
                for x in value
            ]

        if kind == 'int':
            # Make sure value is an integer
            if (isinstance(value, basestring)):
                value = value.replace('%', '')
                value = value.replace('*', '')
            try:
                value = long(value)
            except Exception, e:
                self.log.exception(e)
                raise CoilsException(
                    'Unable to convert search value "{0}" to integer.'.
                    format(value, )
                )
        elif kind == 'date':
            # Deal with date value
            if (not (isinstance(value, datetime))):
                # Translate string to datetime
                value = Parse_Value_To_UTCDateTime(value)
            elif (isinstance(value, int)):
                value = datetime.utcfromtimestamp(value)
            # set timezone to UTC
            value.replace(tzinfo=gettz('UTC'))

        return value

    def _translate_key(self, key, value, keymap, expression='SCALAR', ):
        """
        Transform the key:value pair based on the keymap

        Keymap Example:
            'private':        ['is_private', 'int', ],
            'bossname':       ['boss_name', ],
            'managersname':   ['boss_name', ],
            'managers_name':  ['boss_name', ],
            'sex':            ['gender', ],
            'deathdate':      [grave_date', 'date', None, ],
        This translates the named key into the first value of the corresponding
        array.  If the array has a second value it is: "int" or "date" and the
        value is translated into the corresponding value type.  If the value is
        None and the array has a third value (a "default" value) then the value
        is replaced with the third value.  Date formats supported are
        "YYYY-MM-DD" and "YYYY-MM-DD HH:mm" where hours are in 0 - 23 not
        AM/PM.  All dates are interpreted as UTC.
        """

        key = key.lower()
        if key in keymap:
            x = keymap[key]
            if x is None:
                # TODO: This key is defined as None in the keymap???
                return (None, None)
            # translate key name
            key = x[0]
            # transform value type
            if (len(x) > 1):
                try:
                    pt = type(value)
                    value = self._transform_value(
                        value=value,
                        kind=x[1],
                        enumeration=expression in ('IN', )
                    )
                    if not pt == type(value):
                        self.log.debug(
                            'Coerced type of "{0}" to "{1}" for '
                            'search key "{2}"'
                            .format(pt, type(value), key, )
                        )
                except Exception as exc:
                    raise CoilsException(
                        'Unable to transform value "{0}" into kind "{1}"'
                        ' for expression "{2}"'
                        .format(value, x[1], expression, )
                    )
            # default value, for None
            if ((len(x) == 3) and (value is None)):
                value = x[2]
        else:
            self.log.debug('key {0} not found in entity keymap'.format(key))
        return (key, value, )

    def _form_expression(self, attribute, expression, value):
        if (expression == 'ILIKE'):
            return (attribute.ilike(value.replace('*', '%')))
        elif (expression == 'LIKE'):
            return (attribute.like(value.replace('*', '%')))
        elif (expression in ('NOTEQUALS', 'NE', )):
            return (attribute != value)
        elif (expression == 'GT'):
            return (attribute > value)
        elif (expression == 'LT'):
            return (attribute < value)
        elif (expression == 'IN'):
            return (attribute.in_(value))
        elif (expression == 'ISNULL'):
            return (attribute == None)
        else:
            return (attribute == value)

    def _translate_criterion(self, criterion, entity, keymap):
        '''
        Translates a criterion in the corresponding ORM components

        In this function the criterian is decomponsed to v, k, e, & c.  These
        short variables are:
          v: value k: key (exploded) e: expression c: conjunction
        '''

        # Returns Entity, Key, Conjunction, Expression
        v = criterion.get('value', None)
        try:
            k = criterion['key'].split('.')
        except KeyError:
            raise CoilsException(
                'Criteria does not specify a key: {0}'.format(criterion, )
            )

        # Everything after the first "." needs to be reassembled as the
        # second element, at most we should see a two element list.
        # Property names possibly [ likely ] contain "." characters.
        if (len(k) > 1):
            k[1] = '.'.join(k[1:])
            k = k[0:2]
        c = criterion.get('conjunction', 'AND').upper()
        e = criterion.get('expression', 'EQUALS').upper()

        # Qualify to known/legal expressions
        if (
            e not in
            (
                'EQUALS', 'ILIKE', 'LIKE', 'NOTEQUALS', 'GT', 'LT',
                'IN', 'ISNULL',
            )
        ):
            self.log.error(
                'error in translate_criterion - unsupported expression "{0}"'.
                format(e, )
            )
            return (None, None, None, None, None)

        if (len(k) == 1):
            k = k[0]
            (k, v) = self._translate_key(
                key=k, value=v, keymap=keymap, expression=e,
            )
            if k is not None and (hasattr(entity, k)):
                """Key resolved via keymap"""
                return (entity, k, v, c, e)
            """
            Key not resolved via keymap, we try custom search criteria and
            check for company value support on the entity.
            """
            (x_entity, x_k, x_v, x_c, x_e, ) = (
                self._custom_search_criteria([k, ], v, c, e, )
            )
            if x_entity is not None:
                """
                if _custom_search_criteria returned something then we return
                that - custom search criteria may override company values!
                WARN: custom search criteria may override company value keys!
                """
                return (x_entity, x_k, x_v, x_c, x_e, )
            if hasattr(entity, 'company_values'):
                """
                If the key has not yet been matched and the entity supports
                company_values then we assume the key is the name of a
                CompanyValue
                """
                # company value
                self.log.debug(
                    'Assuming key "{0}" indicates a company value'
                    .format(k, )
                )
                return (CompanyValue, k, v, c, e)
            """No keys resolved, give up. We throw the criteria away!"""
            return (None, None, None, None, None, )
        elif len(k) == 2:
                # address or telephone
                if (
                    hasattr(entity, 'addresses') and
                    (k[0].lower() in ['address'])
                ):
                    k = k[1]
                    (k, v) = self._translate_key(
                        key=k,
                        value=v,
                        keymap=COILS_ADDRESS_KEYMAP,
                        expression=e,
                    )
                    if (k is not None):
                        return (Address, k, v, c, e)
                elif (
                    hasattr(entity, 'telephones') and
                    (k[0].lower() in ['phone', 'telephone'])
                ):
                    k = k[1]
                    (k, v) = self._translate_key(
                        key=k,
                        value=v,
                        keymap=COILS_TELEPHONE_KEYMAP,
                        expression=e,
                    )
                    if (k is not None):
                        return (Telephone, k, v, c, e)
                elif (k[0].lower() in ['property']):
                    if (hasattr(entity, 'properties')):
                        return (ObjectProperty, k[1], v, c, e)
                    else:
                        self.log.warn(
                            'Client issued property search criteria on entity '
                            '{0} that does not support properties.'
                            .format(entity, )
                        )
                        return (None, None, None, None, None)
        return self._custom_search_criteria(k, v, c, e, )

        # WARN: Unreachable code
        # TODO: Provide a default to raise an exception in this case
        self.log.warn(
            'Client issued unknown key {0} in search criteria; discarding.'.
            format('.'.join(k), )
        )

        return (None, None, None, None, None)

    def _custom_search_criteria(self, key, value, conjunction, expression, ):
        return (None, None, None, None, None)

    def _aggregate_criterion(self, aggregation, criterion, entity, keymap):

        # entity, key, value, conjunction, expression
        (E, k, v, c, e) = self._translate_criterion(criterion, entity, keymap)

        if (E is not None):

            if (E not in aggregation):
                aggregation[E] = {}

            if (k not in aggregation[E]):
                aggregation[E][k] = {'AND': [], 'OR': [], }

            '''
            If the value is an integer and the user attempted a LIKE / ILIKE
            expression we turn the expression into an EQUALS to avoid an error
            Also change to equals if it is a GT or LT comparison and the value
            is not-numeric
            '''

            if e in ('IN', ):
                if not isinstance(v, list):
                    self.log.warn(
                        'IN clause attemtepted on a non-list for key "{0}"'.
                        format(k, )
                    )
                    e = 'EQUALS'
                # TODO: check enumeration values against required type

            if (
                isinstance(v, int) and e in ('LIKE', 'ILIKE', )
            ):
                self.log.warn(
                    'Client attempted LIKE/ILIKE on numeric attribute "{0}", '
                    'changing to EQUALS'.
                    format(k, )
                )
                e = 'EQUALS'

            if (
                (not
                    (
                        isinstance(v, int) or
                        isinstance(v, long) or
                        isinstance(v, float) or
                        isinstance(v, datetime)
                    )
                 ) and e in ('GT', 'LT', )
            ):
                self.log.warn(
                    'Client attempted GT/LT on non-numeric attribute "{0}" '
                    'of type "{1}", changing to EQUALS'.
                    format(k, type(k), )
                )
                e = 'EQUALS'

            aggregation[E][k][c].append((e, v, ))

        else:
            self.log.warn(
                'Client search criteria invalid & discarded;'
                'aggregation={0} criterion={1}'.
                format(aggregation, criterion, )
            )
        return aggregation

    def _compile_aggregate(
        self, _aggregate, _entity, _keymap,
    ):

        _cq = {
            'hints': list(),
            'notes': list(),
            'from': {'inner': list(), 'outer': list(), },
            'where': {
                'and': and_(), 'or': or_(), 'notes': list(), }
        }

        for E in _aggregate:
            if (E == _entity):
                for k in _aggregate[E]:
                    for e, v in _aggregate[E][k]['AND']:
                        _cq['where']['and'].append(
                            self._form_expression(getattr(_entity, k), e, v, )
                        )
                    for e, v in _aggregate[E][k]['OR']:
                        _cq['where']['or'].append(
                            self._form_expression(getattr(_entity, k), e, v, )
                        )

            elif (E == CompanyValue):
                # Join for Company criteria
                for k in _aggregate[E]:
                    t = aliased(CompanyValue)
                    _cq['from']['inner'].append(
                        {
                            'target': t,
                            'clause': and_(
                                t.parent_id == _entity.object_id,
                                t.name == k),
                            'from': _entity,
                        }
                    )
                    inner_and = and_()
                    inner_or = or_()
                    for e, v in _aggregate[E][k]['AND']:
                        inner_and.append(
                            self._form_expression(t.string_value, e, v)
                        )
                    for e, v in _aggregate[E][k]['OR']:
                        inner_or.append(
                            self._form_expression(t.string_value, e, v)
                        )
                    if (len(inner_or) > 0):
                        inner_and.append(inner_or)
                    _cq['where']['and'].append(inner_and)

            elif (E == ObjectProperty):
                # Join for ObjectProperty criteria
                for k in _aggregate[E]:
                    (namespace, name) = PropertyManager.Parse_Property_Name(k)
                    t = aliased(ObjectProperty)
                    _cq['from']['outer'].append(
                        {
                            'target': t,
                            'clause': and_(
                                t.parent_id == _entity.object_id,
                                t.name == name,
                                t.namespace == namespace, ),
                            'from': _entity,
                        }
                    )
                    inner_and = and_()
                    inner_or = or_()

                    for e, v in _aggregate[E][k]['AND']:
                        if (isinstance(v, int)):
                            inner_and.append(
                                self._form_expression(t._integer_value, e, v)
                            )
                        else:
                            inner_and.append(
                                self._form_expression(t._string_value, e, v)
                            )
                    for e, v in _aggregate[E][k]['OR']:
                        if (isinstance(v, int)):
                            inner_or.append(
                                self._form_expression(t._integer_value, e, v)
                            )
                        else:
                            inner_or.append(
                                self._form_expression(t._string_value, e, v)
                            )
                    # if (len(inner_or) > 0):
                    #     inner_and.append(inner_or)
                    if (len(inner_or) > 0):
                        _cq['where']['or'].append(inner_or)
                    if (len(inner_and) > 0):
                        _cq['where']['and'].append(inner_and)

            else:
                for k in _aggregate[E]:
                    for e, v in _aggregate[E][k]['AND']:
                        _cq['where']['and'].append(
                            self._form_expression(getattr(E, k), e, v)
                        )
                    for e, v in _aggregate[E][k]['OR']:
                        _cq['where']['or'].append(
                            self._form_expression(getattr(E, k), e, v)
                        )
                _cq['from']['inner'].append(
                    {'target': E,
                     'from': _entity, }
                )

        return _cq

    def _parse_criteria(self, criteria, entity, keymap):

        def add_outer_join_to_query(q, target, clause=None, ):
            if clause is not None:
                q = q.outerjoin(target, clause, )
            else:
                q = q.outerjoin(target)
            return q

        def add_inner_join_to_query(q, target, clause=None, ):
            if clause is not None:
                q = q.join(target, clause, )
            else:
                q = q.join(target)
            return q

        """ Compiles criteria in an ORM query """
        # TODO: Support object properties
        aggregate = dict()
        subaggregates = list()

        # Compile the criteria
        if not isinstance(criteria, list):
            raise CoilsException(
                'Criteria specification of type "{0}" is not understood.'.
                format(type(criteria), )
            )

        for criterion in criteria:
            # Entity, key, value, conjunction, expression
            if 'clause' in criterion:
                tmp = dict()
                self.set_query_debug_value('encountered clause; compiling')
                for clause in criterion['clause']:
                    tmp = self._aggregate_criterion(
                        tmp, clause,  entity, keymap
                    )
                if criterion.get('conjunction', 'AND') == 'AND':
                    subaggregates.append(
                        (self._compile_aggregate(tmp, entity, keymap, ),
                         'and', )
                    )
                else:
                    subaggregates.append(
                        (self._compile_aggregate(tmp, entity, keymap, ),
                         'or', )
                    )
            else:
                aggregate = self._aggregate_criterion(
                    aggregate, criterion,  entity, keymap
                )

        self.set_query_debug_value(aggregate=aggregate)

        _cq = self._compile_aggregate(
            aggregate, entity, keymap,
        )

        # Create query

        db = self._ctx.db_session()
        _query = db.query(entity).with_labels()
        _and = and_()
        _or = or_()

        # constrct FROM clause

        for joinable in _cq['from']['inner']:
            # _query.select_from
            _query = add_inner_join_to_query(
                _query, joinable['target'], joinable.get('clause', None)
            )

        for joinable in _cq['from']['outer']:
            _query = add_outer_join_to_query(
                _query, joinable['target'], joinable.get('clause', None)
            )

        # construct outer "simple" WHERE clause

        for where in _cq['where']['and']:
            _and.append(where)

        for where in _cq['where']['or']:
            _or.append(where)

        # Inject clauses

        for scq, conjunction, in subaggregates:
            for joinable in scq['from']['inner']:
                _query = add_inner_join_to_query(
                    _query, joinable['target'], joinable.get('clause', None)
                )
            for joinable in scq['from']['outer']:
                _query = add_outer_join_to_query(
                    _query, joinable['target'], joinable.get('clause', None)
                )
            scq = None

        for scq, conjunction, in subaggregates:
            s_and = scq['where']['and']
            s_or = scq['where']['or']
            primary = None
            if len(s_or) > 0 and len(s_and) == 0:
                primary = s_or
            elif len(s_or) == 0 and len(s_and) > 0:
                primary = s_and
            elif len(s_or) > 0 and len(s_and) > 0:
                s_or.append(s_and)
                primary = s_or
            if primary is not None:
                if conjunction == 'and':
                    _and.append(primary)
                elif conjunction == 'or':
                    _or.append(primary)

        # Apply WHERE clause to query

        if len(_or) > 0:
            if len(_and) > 0:
                _or.append(_and)
            _query = _query.filter(_or)
        elif len(_and) > 0:
            _query = _query.filter(_and)

        self.set_query_debug_value(query=_query)

        return _query

    def do_revolve(self):
        return []

    def disable_revolve(self):
        self._revolve = False

    def set_return_value(self, data):
        if (isinstance(data, list)):
            if (self.access_check):
                data = self._ctx.access_manager.filter_by_access('r', data, )
            if (len(data) > 0):
                if (self.mode == RETRIEVAL_MODE_SINGLE):
                    self._result = data[0]
                else:
                    if (len(data) > self._limit):
                        data = data[0:self._limit]
                    self._result = data
                    if self._revolve:
                        self.disable_revolve()  # Avoid revolving loops
                        self._result.extend(self.do_revolve())
            elif (self.mode == RETRIEVAL_MODE_MULTIPLE):
                self._result = []
            elif (self.mode == RETRIEVAL_MODE_SINGLE):
                self._result = None
            else:
                raise CoilsException('Unknown mode value')
            return
        raise CoilsException('Data for Get result is not a list')
        self._result = None

    def set_query_debug_value(
        self,
        query=None,
        aggregate=None,
        compiled_query=None,
        message=None,
    ):
        if not hasattr(self, '_query_debug_values'):
            self._query_debug_values = dict()

        if query is not None:
            self._query_debug_values['query'] = query
        if aggregate is not None:
            self._query_debug_values['aggregate'] = aggregate
        if compiled_query is not None:
            self._query_debug_values['compiledquery'] = compiled_query
        if message is not None:
            if 'messages' not in self._query_debug_values:
                self._query_debug_value['messages'] = list()
            self._query_debug_value['messages'].append(message)

    def get_query_debug_value(self, value):

        if not hasattr(self, '_query_debug_values'):
            self._query_debug_values = dict()

        if value == 'query':
            return self._query_debug_values['query']
        elif value == 'aggregate':
            return self._query_debug_values['aggregate']
        elif value == 'compiled_query':
            return self._query_debug_values['compiled_query']
        else:
            if 'messages' in self._query_debug_values:
                return self._query_debug_values['messages']
            return list()

    def _apply_sort_criteria(
        self, query, entity, keymap, sort_keys, reverse_order=False,
    ):
        if not sort_keys:
            return query
        sort_fields = list()
        for field_name in sort_keys:
            if field_name in keymap:
                field_name = keymap.get(field_name)[0]
            if hasattr(entity, field_name):
                if not reverse_order:
                    sort_fields.append(asc(getattr(entity, field_name)))
                else:
                    sort_fields.append(desc(getattr(entity, field_name)))
        if sort_fields:
            query = query.order_by(*sort_fields)
        return query
