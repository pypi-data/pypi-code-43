# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import doctest
import inspect
import operator
import os
import subprocess
import sys
import time
import unittest
from functools import reduce
from functools import wraps
from itertools import chain
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

from lxml import etree
from sql import Table

from trytond.pool import Pool, isregisteredby
from trytond import backend
from trytond.model import Workflow, ModelSQL, ModelSingleton, ModelView, fields
from trytond.model.fields import get_eval_fields, Function
from trytond.tools import is_instance_method
from trytond.transaction import Transaction
from trytond.cache import Cache
from trytond.config import config, parse_uri
from trytond.wizard import StateView, StateAction
from trytond.pyson import PYSONDecoder

__all__ = ['DB_NAME', 'USER', 'CONTEXT',
    'activate_module', 'ModuleTestCase', 'with_transaction',
    'doctest_setup', 'doctest_teardown', 'doctest_checker',
    'suite', 'all_suite', 'modules_suite']

Pool.start()
USER = 1
CONTEXT = {}
DB_NAME = os.environ['DB_NAME']
DB_CACHE = os.environ.get('DB_CACHE')
Pool.test = True


def activate_module(modules):
    '''
    Activate modules for the tested database
    '''
    if isinstance(modules, str):
        modules = [modules]
    name = '-'.join(modules)
    if not db_exist(DB_NAME) and restore_db_cache(name):
        return
    create_db()
    with Transaction().start(DB_NAME, 1, close=True) as transaction:
        pool = Pool()
        Module = pool.get('ir.module')

        records = Module.search([
                ('name', 'in', modules),
                ])
        assert len(records) == len(modules)

        records = Module.search([
                ('name', 'in', modules),
                ('state', '!=', 'activated'),
                ])

        if records:
            Module.activate(records)
            transaction.commit()

            ActivateUpgrade = pool.get('ir.module.activate_upgrade',
                type='wizard')
            instance_id, _, _ = ActivateUpgrade.create()
            transaction.commit()
            ActivateUpgrade(instance_id).transition_upgrade()
            ActivateUpgrade.delete(instance_id)
            transaction.commit()
    backup_db_cache(name)


def restore_db_cache(name):
    result = False
    if DB_CACHE:
        backend_name = backend.name()
        cache_file = _db_cache_file(DB_CACHE, name, backend_name)
        if os.path.exists(cache_file):
            if backend_name == 'sqlite':
                result = _sqlite_copy(cache_file, restore=True)
            elif backend_name == 'postgresql':
                result = _pg_restore(cache_file)
    if result:
        Pool(DB_NAME).init()
    return result


def backup_db_cache(name):
    if DB_CACHE:
        if not os.path.exists(DB_CACHE):
            os.makedirs(DB_CACHE)
        backend_name = backend.name()
        cache_file = _db_cache_file(DB_CACHE, name, backend_name)
        if not os.path.exists(cache_file):
            if backend_name == 'sqlite':
                _sqlite_copy(cache_file)
            elif backend_name == 'postgresql':
                _pg_dump(cache_file)


def _db_cache_file(path, name, backend_name):
    return os.path.join(path, '%s-%s.dump' % (name, backend_name))


def _sqlite_copy(file_, restore=False):
    import sqlite3 as sqlite

    with Transaction().start(DB_NAME, 0) as transaction, \
            sqlite.connect(file_) as conn2:
        conn1 = transaction.connection
        # sqlitebck does not work with pysqlite2
        if not isinstance(conn1, sqlite.Connection):
            return False
        if restore:
            conn2, conn1 = conn1, conn2
        if hasattr(conn1, 'backup'):
            conn1.backup(conn2)
        else:
            try:
                import sqlitebck
            except ImportError:
                return False
            sqlitebck.copy(conn1, conn2)
    return True


def _pg_options():
    uri = parse_uri(config.get('database', 'uri'))
    options = []
    env = os.environ.copy()
    if uri.hostname:
        options.extend(['-h', uri.hostname])
    if uri.port:
        options.extend(['-p', str(uri.port)])
    if uri.username:
        options.extend(['-U', uri.username])
    if uri.password:
        env['PGPASSWORD'] = uri.password
    return options, env


def _pg_restore(cache_file):
    with Transaction().start(
            None, 0, close=True, autocommit=True) as transaction:
        transaction.database.create(transaction.connection, DB_NAME)
    cmd = ['pg_restore', '-d', DB_NAME]
    options, env = _pg_options()
    cmd.extend(options)
    cmd.append(cache_file)
    try:
        return not subprocess.call(cmd, env=env)
    except OSError:
        cache_name, _ = os.path.splitext(os.path.basename(cache_file))
        cache_name = backend.get('TableHandler').convert_name(cache_name)
        with Transaction().start(
                None, 0, close=True, autocommit=True) as transaction:
            transaction.database.drop(transaction.connection, DB_NAME)
            transaction.database.create(
                transaction.connection, DB_NAME, cache_name)
        return True


def _pg_dump(cache_file):
    cmd = ['pg_dump', '-f', cache_file, '-F', 'c']
    options, env = _pg_options()
    cmd.extend(options)
    cmd.append(DB_NAME)
    try:
        return not subprocess.call(cmd, env=env)
    except OSError:
        cache_name, _ = os.path.splitext(os.path.basename(cache_file))
        cache_name = backend.get('TableHandler').convert_name(cache_name)
        # Ensure any connection is left open
        backend.get('Database')(DB_NAME).close()
        with Transaction().start(
                None, 0, close=True, autocommit=True) as transaction:
            transaction.database.create(
                transaction.connection, cache_name, DB_NAME)
        open(cache_file, 'a').close()
        return True


def with_transaction(user=1, context=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            transaction = Transaction()
            with transaction.start(DB_NAME, user, context=context):
                try:
                    result = func(*args, **kwargs)
                finally:
                    transaction.rollback()
                    # Drop the cache as the transaction is rollbacked
                    Cache.drop(DB_NAME)
                return result
        return wrapper
    return decorator


class ModuleTestCase(unittest.TestCase):
    'Trytond Test Case'
    module = None
    extras = None

    @classmethod
    def setUpClass(cls):
        drop_db()
        modules = [cls.module]
        if cls.extras:
            modules.extend(cls.extras)
        activate_module(modules)
        super(ModuleTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(ModuleTestCase, cls).tearDownClass()
        drop_db()

    @with_transaction()
    def test_rec_name(self):
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            # Skip testing default value even if the field doesn't exist
            # as there is a fallback to id
            if model._rec_name == 'name':
                continue
            assert model._rec_name in model._fields, (
                'Wrong _rec_name "%s" for %s'
                % (model._rec_name, mname))
            field = model._fields[model._rec_name]
            assert field._type in {'char', 'text'}, (
                "Wrong '%s' type for _rec_name of %s'"
                % (field._type, mname))

    @with_transaction()
    def test_view(self):
        'Test validity of all views of the module'
        pool = Pool()
        View = pool.get('ir.ui.view')
        views = View.search([
                ('module', '=', self.module),
                ('model', '!=', ''),
                ])
        for view in views:
            if view.inherit and view.inherit.model == view.model:
                view_id = view.inherit.id
            else:
                view_id = view.id
            model = view.model
            Model = pool.get(model)
            res = Model.fields_view_get(view_id)
            assert res['model'] == model
            tree = etree.fromstring(res['arch'])

            validator = etree.RelaxNG(etree=View.get_rng(res['type']))
            # Don't use assert_ because 2to3 convert to assertTrue
            validator.assertValid(tree)

            tree_root = tree.getroottree().getroot()

            for element in tree_root.iter():
                if element.tag in ('field', 'label', 'separator', 'group'):
                    for attr in ('name', 'icon'):
                        field = element.get(attr)
                        if field:
                            assert field in res['fields'], (
                                'Missing field: %s' % field)
                if element.tag == 'button':
                    button_name = element.get('name')
                    assert button_name in Model._buttons, (
                        "Button '%s' is not in %s._buttons"
                        % (button_name, Model.__name__))

    @with_transaction()
    def test_rpc_callable(self):
        'Test that RPC methods are callable'
        for _, model in Pool().iterobject():
            for method_name in model.__rpc__:
                assert callable(getattr(model, method_name, None)), (
                    "'%s' is not callable on '%s'"
                    % (method_name, model.__name__))

    @with_transaction()
    def test_depends(self):
        'Test for missing depends'
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            for fname, field in model._fields.items():
                fields = set()
                fields |= get_eval_fields(field.domain)
                if hasattr(field, 'digits'):
                    fields |= get_eval_fields(field.digits)
                if hasattr(field, 'add_remove'):
                    fields |= get_eval_fields(field.add_remove)
                if hasattr(field, 'size'):
                    fields |= get_eval_fields(field.size)
                fields.discard(fname)
                fields.discard('context')
                fields.discard('_user')
                depends = set(field.depends)
                assert fields <= depends, (
                    'Missing depends %s in "%s"."%s"' % (
                        list(fields - depends), mname, fname))
                assert depends <= set(model._fields), (
                    'Unknown depends %s in "%s"."%s"' % (
                        list(depends - set(model._fields)), mname, fname))
            if issubclass(model, ModelView):
                for bname, button in model._buttons.items():
                    depends = set(button.get('depends', []))
                    assert depends <= set(model._fields), (
                        'Unknown depends %s in button "%s"."%s"' % (
                            list(depends - set(model._fields)), mname, bname))

    @with_transaction()
    def test_depends_parent(self):
        "Test depends on _parent_ contains also the parent relation"
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            for fname, field in model._fields.items():
                for attribute in ['depends', 'on_change', 'on_change_with',
                        'selection_change_with', 'autocomplete']:
                    depends = getattr(field, attribute, [])
                    for depend in depends:
                        prefix = []
                        for d in depend.split('.'):
                            if d.startswith('_parent_'):
                                relation = '.'.join(
                                    prefix + [d[len('_parent_'):]])
                                assert relation in depends, (
                                    'Missing "%s" in "%s"."%s"."%s"' % (
                                        relation, mname, fname, attribute))
                            prefix.append(d)

    @with_transaction()
    def test_field_methods(self):
        'Test field methods'
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            for attr in dir(model):
                for prefixes in [['default_'],
                        ['on_change_', 'on_change_with_'],
                        ['order_'], ['domain_'], ['autocomplete_']]:
                    if attr == 'on_change_with':
                        continue
                    # TODO those method should be renamed
                    if attr == 'default_get':
                        continue
                    if mname == 'ir.rule' and attr == 'domain_get':
                        continue

                    # Skip if it is a field
                    if attr in model._fields:
                        continue
                    fnames = [attr[len(prefix):] for prefix in prefixes
                        if attr.startswith(prefix)]
                    if not fnames:
                        continue
                    assert any(f in model._fields for f in fnames), (
                        'Field method "%s"."%s" for unknown field' % (
                            mname, attr))

                    if attr.startswith('default_'):
                        fname = attr[len('default_'):]
                        if isinstance(model._fields[fname], fields.MultiValue):
                            try:
                                getattr(model, attr)(pattern=None)
                            # get_multivalue may raise an AttributeError
                            # if pattern is not defined on the model
                            except AttributeError:
                                pass
                        else:
                            getattr(model, attr)()
                    elif attr.startswith('order_'):
                        tables = {None: (model.__table__(), None)}
                        getattr(model, attr)(tables)
                    elif any(attr.startswith(p) for p in [
                                'on_change_',
                                'on_change_with_',
                                'autocomplete_']):
                        record = model()
                        getattr(record, attr)()

    @with_transaction()
    def test_menu_action(self):
        'Test that menu actions are accessible to menu\'s group'
        pool = Pool()
        Menu = pool.get('ir.ui.menu')
        ModelData = pool.get('ir.model.data')

        module_menus = ModelData.search([
                ('model', '=', 'ir.ui.menu'),
                ('module', '=', self.module),
                ])
        menus = Menu.browse([mm.db_id for mm in module_menus])
        for menu, module_menu in zip(menus, module_menus):
            if not menu.action_keywords:
                continue
            menu_groups = set(menu.groups)
            actions_groups = reduce(operator.or_,
                (set(k.action.groups) for k in menu.action_keywords
                    if k.keyword == 'tree_open'))
            if not actions_groups:
                continue
            assert menu_groups <= actions_groups, (
                'Menu "%(menu_xml_id)s" actions are not accessible to '
                '%(groups)s' % {
                    'menu_xml_id': module_menu.fs_id,
                    'groups': ','.join(g.name
                        for g in menu_groups - actions_groups),
                    })

    @with_transaction()
    def test_model_access(self):
        'Test missing default model access'
        pool = Pool()
        Access = pool.get('ir.model.access')
        no_groups = {a.model.name for a in Access.search([
                    ('group', '=', None),
                    ])}
        with_groups = {a.model.name for a in Access.search([
                    ('group', '!=', None),
                    ])}

        assert no_groups >= with_groups, (
            'Model "%(models)s" are missing a default access' % {
                'models': list(with_groups - no_groups),
                })

    @with_transaction()
    def test_workflow_transitions(self):
        'Test all workflow transitions exist'
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            if not issubclass(model, Workflow):
                continue
            field = getattr(model, model._transition_state)
            if isinstance(field.selection, (tuple, list)):
                values = field.selection
            else:
                # instance method may not return all the possible values
                if is_instance_method(model, field.selection):
                    continue
                values = getattr(model, field.selection)()
            states = set(dict(values))
            transition_states = set(chain(*model._transitions))
            assert transition_states <= states, (
                ('Unknown transition states "%(states)s" '
                    'in model "%(model)s". ') % {
                    'states': list(transition_states - states),
                    'model': model.__name__,
                    })

    @with_transaction()
    def test_wizards(self):
        'Test wizards are correctly defined'
        for wizard_name, wizard in Pool().iterobject(type='wizard'):
            if not isregisteredby(wizard, self.module, type_='wizard'):
                continue
            session_id, start_state, _ = wizard.create()
            assert start_state in wizard.states, ('Unknown start state '
                '"%(state)s" on wizard "%(wizard)s"' % {
                    'state': start_state,
                    'wizard': wizard_name,
                    })
            wizard_instance = wizard(session_id)
            for state_name, state in wizard_instance.states.items():
                if isinstance(state, StateView):
                    # Don't test defaults as they may depend on context
                    state.get_view(wizard_instance, state_name)
                    state.get_buttons(wizard_instance, state_name)
                if isinstance(state, StateAction):
                    state.get_action()

    @with_transaction()
    def test_selection_fields(self):
        'Test selection values'
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            for field_name, field in model._fields.items():
                selection = getattr(field, 'selection', None)
                if selection is None:
                    continue
                selection_values = field.selection
                if not isinstance(selection_values, (tuple, list)):
                    sel_func = getattr(model, field.selection)
                    if not is_instance_method(model, field.selection):
                        selection_values = sel_func()
                    else:
                        record = model()
                        selection_values = sel_func(record)
                assert all(len(v) == 2 for v in selection_values), (
                    'Invalid selection values "%(values)s" on field '
                    '"%(field)s" of model "%(model)s"' % {
                        'values': selection_values,
                        'field': field_name,
                        'model': model.__name__,
                        })

    @with_transaction()
    def test_function_fields(self):
        "Test function fields methods"
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            for field_name, field in model._fields.items():
                if not isinstance(field, Function):
                    continue
                for func_name in [field.getter, field.setter, field.searcher]:
                    if not func_name:
                        continue
                    assert getattr(model, func_name, None), (
                        "Missing method '%(func_name)s' "
                        "on model '%(model)s' for field '%(field)s" % {
                            'func_name': func_name,
                            'model': model.__name__,
                            'field': field_name,
                            })

    @with_transaction()
    def test_ir_action_window(self):
        'Test action windows are correctly defined'
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        ActionWindow = pool.get('ir.action.act_window')
        for model_data in ModelData.search([
                    ('module', '=', self.module),
                    ('model', '=', 'ir.action.act_window'),
                    ]):
            action_window = ActionWindow(model_data.db_id)
            if not action_window.res_model:
                continue
            Model = pool.get(action_window.res_model)
            for active_id, active_ids in [
                    (None, []),
                    (1, [1]),
                    (1, [1, 2]),
                    ]:
                decoder = PYSONDecoder({
                        'active_id': active_id,
                        'active_ids': active_ids,
                        'active_model': action_window.res_model,
                        })
                domain = decoder.decode(action_window.pyson_domain)
                order = decoder.decode(action_window.pyson_order)
                context = decoder.decode(action_window.pyson_context)
                search_value = decoder.decode(action_window.pyson_search_value)
                if action_window.context_domain:
                    domain = ['AND', domain,
                        decoder.decode(action_window.context_domain)]
                with Transaction().set_context(context):
                    Model.search(
                        domain, order=order, limit=action_window.limit)
                    if search_value:
                        Model.search(search_value)
                for action_domain in action_window.act_window_domains:
                    if not action_domain.domain:
                        continue
                    Model.search(decoder.decode(action_domain.domain))
            if action_window.context_model:
                pool.get(action_window.context_model)

    @with_transaction()
    def test_modelsingleton_inherit_order(self):
        'Test ModelSingleton, ModelSQL, ModelStorage order in the MRO'
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            if (not issubclass(model, ModelSingleton)
                    or not issubclass(model, ModelSQL)):
                continue
            mro = inspect.getmro(model)
            singleton_index = mro.index(ModelSingleton)
            sql_index = mro.index(ModelSQL)
            assert singleton_index < sql_index, (
                "ModelSingleton must appear before ModelSQL in the parent "
                "classes of '%s'." % mname)

    @with_transaction()
    def test_buttons_registered(self):
        'Test all buttons are registered in ir.model.button'
        pool = Pool()
        Button = pool.get('ir.model.button')
        for mname, model in Pool().iterobject():
            if not isregisteredby(model, self.module):
                continue
            if not issubclass(model, ModelView):
                continue
            ir_buttons = {b.name for b in Button.search([
                        ('model.model', '=', model.__name__),
                        ])}
            buttons = set(model._buttons)
            assert ir_buttons >= buttons, (
                'The buttons "%(buttons)s" of Model "%(model)s" are not '
                'registered in ir.model.button.' % {
                    'buttons': list(buttons - ir_buttons),
                    'model': model.__name__,
                    })

    @with_transaction()
    def test_buttons_states(self):
        "Test the states of buttons"
        pool = Pool()
        keys = {'readonly', 'invisible', 'icon', 'pre_validate', 'depends'}
        for mname, model in pool.iterobject():
            if not isregisteredby(model, self.module):
                continue
            if not issubclass(model, ModelView):
                continue
            for button, states in model._buttons.items():
                assert set(states).issubset(keys), (
                    'The button "%(button)s" of Model "%(model)s" has extra '
                    'keys "%(keys)s".' % {
                        'button': button,
                        'model': mname,
                        'keys': set(states) - keys,
                        })


def db_exist(name=DB_NAME):
    Database = backend.get('Database')
    database = Database().connect()
    return name in database.list()


def create_db(name=DB_NAME, lang='en'):
    Database = backend.get('Database')
    if not db_exist(name):
        database = Database()
        database.connect()
        connection = database.get_connection(autocommit=True)
        try:
            database.create(connection, name)
        finally:
            database.put_connection(connection, True)

        database = Database(name)
        connection = database.get_connection()
        try:
            with connection.cursor() as cursor:
                database.init()
                ir_configuration = Table('ir_configuration')
                cursor.execute(*ir_configuration.insert(
                        [ir_configuration.language], [[lang]]))
            connection.commit()
        finally:
            database.put_connection(connection)

        pool = Pool(name)
        pool.init(update=['res', 'ir'], lang=[lang])
        with Transaction().start(name, 0):
            User = pool.get('res.user')
            Lang = pool.get('ir.lang')
            language, = Lang.search([('code', '=', lang)])
            language.translatable = True
            language.save()
            users = User.search([('login', '!=', 'root')])
            User.write(users, {
                    'language': language.id,
                    })
            Module = pool.get('ir.module')
            Module.update_list()


def drop_db(name=DB_NAME):
    if db_exist(name):
        Database = backend.get('Database')
        database = Database(name)
        database.close()

        with Transaction().start(
                None, 0, close=True, autocommit=True) as transaction:
            database.drop(transaction.connection, name)
            Pool.stop(name)
            Cache.drop(name)


def drop_create(name=DB_NAME, lang='en'):
    if db_exist(name):
        drop_db(name)
    create_db(name, lang)


def doctest_setup(test):
    return drop_create()


def doctest_teardown(test):
    return drop_db()


doctest_checker = doctest.OutputChecker()


class TestSuite(unittest.TestSuite):
    def run(self, *args, **kwargs):
        DatabaseOperationalError = backend.get('DatabaseOperationalError')
        while True:
            try:
                exist = db_exist()
                break
            except DatabaseOperationalError as err:
                # Retry on connection error
                sys.stderr.write(str(err))
                time.sleep(1)
        result = super(TestSuite, self).run(*args, **kwargs)
        if not exist:
            drop_db()
        return result


def suite():
    '''
    Return test suite for other modules
    '''
    return TestSuite()


def all_suite(modules=None):
    '''
    Return all tests suite of current module
    '''
    suite_ = suite()

    def add_tests(filename, module_prefix):
        if not (filename.startswith('test_') and filename.endswith('.py')):
            return
        if modules and fn[:-3] not in modules:
            return
        modname = module_prefix + '.' + filename[:-3]
        __import__(modname)
        module = sys.modules[modname]
        suite_.addTest(module.suite())

    for fn in os.listdir(os.path.dirname(__file__)):
        add_tests(fn, 'trytond.tests')
    if pkg_resources is not None:
        entry_points = pkg_resources.iter_entry_points('trytond.tests')
        for test_entry_point in entry_points:
            base_location = os.path.join(
                test_entry_point.dist.location,
                *test_entry_point.module_name.split('.'))
            for fn in os.listdir(base_location):
                add_tests(fn, test_entry_point.module_name)

    return suite_


def modules_suite(modules=None, doc=True):
    '''
    Return all tests suite of all modules
    '''
    if modules:
        suite_ = suite()
    else:
        suite_ = all_suite()
    from trytond.modules import create_graph, get_module_list, import_module
    graph = create_graph(get_module_list())
    for node in graph:
        module = node.name
        if modules and module not in modules:
            continue
        test_module = 'trytond.modules.%s.tests' % module
        try:
            test_mod = import_module(module, test_module)
        except ImportError:
            continue
        for test in test_mod.suite():
            if isinstance(test, doctest.DocTestCase) and not doc:
                continue
            suite_.addTest(test)
    return suite_
