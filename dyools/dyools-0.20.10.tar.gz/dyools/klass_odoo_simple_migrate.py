from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging
import pprint

from odoorpc.error import RPCError

from .klass_counter import Counter
from .klass_offset_limit import OffsetLimit
from .klass_print import Print

logger = logging.getLogger(__name__)
READ_CREATE_OR_WRITE = 'ReadCreateOrWrite'
EXPORT_IMPORT_XMLID = 'ExportImportXmlID'
REQUIRE_EXACT, REQUIRE_SUP, REQUIRE_SUP_OR_EXACT = 'exact', 'sup', 'exact_or_sup'
REQUIRES = [REQUIRE_EXACT, REQUIRE_SUP, REQUIRE_SUP_OR_EXACT]


def _get_domain_from(line, fnames):
    domain = []
    for fname in fnames:
        domain.append((fname, '=', line[fname]))
    return domain


def clean_data_from_create_write(obj, src, dest, fields, line):
    for k, v in line.items():
        for fname, f_spec in fields.items():
            if fname != k:
                continue
            if f_spec.get('type') == 'many2one':
                if v:
                    try:
                        res_data = dest.env[f_spec.get('relation')].name_search(v[1], operator='=', limit=1)
                        res_data = [x[0] for x in res_data]
                    except RPCError:
                        res_data = dest.env[f_spec.get('relation')].search([('name', '=', v[1])])
                    if len(res_data) == 1:
                        line[fname] = res_data[0]
                    else:
                        Print.error(
                            'error when searching the record model=<{}> field=<{}> value=<{}> results={}'.format(
                                f_spec.get('relation'),
                                fname,
                                v[1],
                                res_data
                            ))
                        if obj._debug:
                            Print.debug('data = {}'.format(pprint.pformat(line)))
                else:
                    line[fname] = False
            if f_spec.get('type') == 'many2many':
                v = v or []
                src_data = src.env[f_spec.get('relation')].browse(v).name_get()
                res_ids = []
                for res_id, res_name in src_data:
                    try:
                        dest_data = dest.env[f_spec.get('relation')].name_search(res_name, operator='=', limit=1)
                        dest_data = [x[0] for x in dest_data]
                    except RPCError:
                        dest_data = dest.env[f_spec.get('relation')].search([('name', '=', res_name)])
                    if len(dest_data) == 1:
                        res_ids.append(dest_data[0])
                    else:
                        Print.error(
                            'error when seraching the record model=<{}> field=<{}> value=<{}> results={}'.format(
                                f_spec.get('relation'),
                                fname,
                                v[1],
                                dest_data
                            ))
                line[fname] = [(6, 0, res_ids)]
    return line


def apply_strategy_on_fields(fields, fnames, strategy, many2x_with_names):
    ff = set()
    for fname, f_spec in fields.items():
        if fname not in fnames:
            continue
        if f_spec.get('type') in ['many2one', 'many2many']:
            if strategy == EXPORT_IMPORT_XMLID:
                if fname not in many2x_with_names:
                    fname = '{}/id'.format(fname)
        ff.add(fname)
    return list(ff)


def all_fields(fields, dest_fields, exclude_fields, include_fields):
    exclude_fields = exclude_fields or []
    include_fields = include_fields or []
    ff = set(['id'])
    for f_name, f_spec in fields.items():
        if f_name in exclude_fields:
            continue
        if f_name not in dest_fields:
            continue
        if f_name in ['__last_update', 'write_date', 'write_uid', 'create_date', 'create_uid']:
            if f_name not in include_fields:
                continue
        if not f_spec.get('store'):
            continue
        if f_spec.get('type') == 'one2many':
            continue
        ff.add(f_name)
    return list(ff)


class OdooSimpleMigrate(object):

    def __init__(self, src, dest):
        self._src = src
        self._dest = dest
        self._counter = Counter()

    def migrate(self,
                model=None,
                src_model=None,
                dest_model=None,
                src_context=None,
                dest_context=None,
                based_on_fields=[],
                fields=None,
                exclude_fields=[],
                include_fields=[],
                many2x_with_names=[],
                domain=[],
                limit=0,
                offset=0,
                order=None,
                by=None,
                debug=False,
                require=False,
                ):
        kwargs = {}
        if offset: kwargs['offset'] = offset
        if limit: kwargs['limit'] = limit
        if order: kwargs['order'] = order
        self._kwargs = kwargs
        self._src_model = src_model or model
        self._dest_model = dest_model or model
        _src_context = self._src.env.context.copy()
        _src_context.update(src_context or {})
        self._src_context = _src_context
        _dest_context = self._dest.env.context.copy()
        _dest_context.update(dest_context or {})
        self._dest_context = _dest_context
        self._fields_specs = self._src.env[self._src_model].fields_get(fields)
        self._fields = all_fields(
            self._fields_specs,
            dest_fields=list(self._dest.env[self._dest_model].fields_get().keys()),
            exclude_fields=exclude_fields,
            include_fields=include_fields,
        )
        self._based_on_fields = list(filter(lambda x: x in self._fields, based_on_fields or []))
        self._strategy = READ_CREATE_OR_WRITE if self._based_on_fields else EXPORT_IMPORT_XMLID
        self._fields = apply_strategy_on_fields(
            fields=self._fields_specs,
            fnames=self._fields,
            strategy=self._strategy,
            many2x_with_names=many2x_with_names,
        )
        self._domain = domain
        self._order = order
        Print.info('counting records from the model <{}>'.format(self._src_model))
        self._count = self._src.env[self._src_model].with_context(self._src_context).search(self._domain, count=True,
                                                                                            **self._kwargs)
        self._by = by or self._count
        assert require in ([False] + REQUIRES), 'The require should be in the list %s' % REQUIRES
        self._require = require
        self._debug = debug
        self._migrate()

    def _migrate(self):
        kwargs = dict()
        if self._order:
            kwargs['order'] = self._order
        if self._debug:
            Print.debug('header : {}'.format(pprint.pformat(self._fields)))
        Print.info('processing migration from model <{}> to <{}> count={} strategy=<{}> require=<{}>'.format(
            self._src_model,
            self._dest_model,
            self._count,
            self._strategy,
            self._require,
        ))
        for offset, limit in OffsetLimit(0, self._by, self._count):
            kwargs.update(dict(offset=offset, limit=limit))
            data = self._src.env[self._src_model].with_context(self._src_context).search(self._domain, **kwargs)
            if isinstance(data, list):
                data = self._src.env[self._src_model].with_context(self._src_context).browse(data)
            if self._strategy == EXPORT_IMPORT_XMLID:
                data = data.export_data(self._fields, raw_data=False)
                if self._debug:
                    Print.debug('data : {}'.format(pprint.pformat(data['datas'])))
                res = self._dest.env[self._dest_model].with_context(self._dest_context).load(self._fields,
                                                                                             data['datas'])
                if not res.get('ids'):
                    Print.error(res)
                if self._debug:
                    Print.debug('result ids : {}'.format(pprint.pformat(res.get('ids'))))
            else:
                data = data.read(self._fields)
                if self._debug:
                    Print.debug('data : {}'.format(pprint.pformat(data)))
                for line in data:
                    line = clean_data_from_create_write(self, self._src, self._dest, self._fields_specs, line)
                    based_on_domain = _get_domain_from(line, self._based_on_fields)
                    exists = self._dest.env[self._dest_model].with_context(self._dest_context).search(based_on_domain)
                    if isinstance(exists, list):
                        exists = self._dest.env[self._dest_model].with_context(self._dest_context).browse(exists)
                    if len(exists) == 1:
                        exists.with_context(self._dest_context).write(line)
                        if self._debug:
                            Print.debug('updating the record model={} ids={}'.format(self._dest_model, exists.ids))
                    elif exists:
                        Print.error('found many records for model={} domain={} ids={}'.format(
                            self._dest_model,
                            based_on_domain,
                            exists.ids,
                        ))
                    else:
                        exists = self._dest.env[self._dest_model].with_context(self._dest_context).create(line)
                        if self._debug:
                            Print.debug('creating a new record model={} ids={}'.format(self._dest_model, exists))
            self._counter.print(
                title='progression: [{}-{}]/{} model from <{}> to <{}>'.format(offset, offset + limit, self._count,
                                                                               self._src_model, self._dest_model))
        Print.info('processing finished for model <{}> to <{}> total migrated={} item(s)'.format(self._src_model, self._dest_model, self._count))
        if self._require:
            nb_items = self._dest.env[self._dest_model].with_context(self._dest_context).search(self._domain,
                                                                                                count=True,
                                                                                                **self._kwargs)
            if (self._require == REQUIRE_EXACT and self._count != nb_items) or (
                    self._require == REQUIRE_SUP and self._count >= nb_items) or (
                    self._require == REQUIRE_SUP_OR_EXACT and self._count > nb_items):
                Print.error('error: required: ({} item(s) of model <{}>), found: ({} item(s) of model <{}>)'.format(
                    self._count, self._src_model, nb_items, self._dest_model
                ))
