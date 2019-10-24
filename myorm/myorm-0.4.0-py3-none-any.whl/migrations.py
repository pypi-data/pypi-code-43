#!/usr/bin/env python
# coding: utf-8

import importlib
import os
import sys

from collections import defaultdict
from pprint import pformat

from datetime import datetime

from myorm.dbobject import DbObject
from myorm.fields import BooleanField, CharField, DateTimeField, ForeignKey, IntegerField, PkField, TextField

field_types = [BooleanField, CharField, DateTimeField, ForeignKey, IntegerField, PkField, TextField]
field_dict = {field.__name__: field for field in field_types}


class Migration:
    migration_dir = None

    def __init__(self):
        self.tablename = 'myorm_migrations'
        self.adaptor = DbObject.adaptor
        self.managed_models = DbObject.managed_models
        self.ref_models = {model.__name__: model for model in self.managed_models}
        self.current_model_state = {}
        self.adaptor.create_migration_table()
        self.render_current_model_state()
        sys.path.append(self.migration_dir)

    def render_current_model_state(self):
        for model in self.managed_models:
            instance = model()
            class_name = instance.__class__.__name__
            self.current_model_state[class_name] = {'tablename': model.tablename, 'fields': []}
            for field in instance.fields:
                field_attrs = {}
                if getattr(field, 'default', None) is not None:
                    field_attrs['default'] = getattr(field, 'default', None)
                if getattr(field, 'max_length', None) is not None:
                    field_attrs['max_length'] = getattr(field, 'max_length', None)
                if getattr(field, 'reference_class', None) is not None:
                    ref_obj = getattr(field, 'reference_class', None)
                    field_attrs['reference_class'] = ref_obj.__name__
                self.current_model_state[class_name]['fields'].append(
                    {field.fieldname: {
                        'field_type': field.__class__.__name__,
                        'field_attrs': field_attrs
                    }}
                )

        return self.current_model_state

    def get_field_changes(self, old_state, new_state):
        fields_to_add = defaultdict(list)
        fields_to_remove = defaultdict(list)

        models_to_check = new_state.keys() & old_state.keys()
        for model in models_to_check:
            old_field_dict = {}
            old_state_field_names = set()
            for field in old_state[model]['fields']:
                for key, value in field.items():
                    old_state_field_names.add(key)
                    old_field_dict[key] = value

            new_field_dict = {}
            new_state_field_names = set()
            for field in new_state[model]['fields']:
                for key, value in field.items():
                    new_state_field_names.add(key)
                    new_field_dict[key] = value

            new_fields = new_state_field_names - old_state_field_names
            dispensable_fields = old_state_field_names - new_state_field_names

            for field in new_fields:
                fields_to_add[model].append({field: new_field_dict[field]})

            for field in dispensable_fields:
                fields_to_remove[model].append({field: old_field_dict[field]})
        return (dict(fields_to_add), dict(fields_to_remove))

    def render_actions(self, old_state, new_state):
        actions = {}
        models_to_create = {model: new_state[model] for model in (new_state.keys() - old_state.keys())}
        if models_to_create:
            actions['creations'] = models_to_create

        models_to_delete = {model: old_state[model] for model in (old_state.keys() - new_state.keys())}
        if models_to_delete:
            actions['deletions'] = models_to_delete

        fields_to_add, fields_to_remove = self.get_field_changes(old_state, new_state)

        if fields_to_add:
            actions['fields_to_add'] = fields_to_add
        if fields_to_remove:
            actions['fields_to_remove'] = fields_to_remove
        return actions

    def get_existing_migration_files(self):
        existing_migration_files = []
        for f in os.listdir(self.migration_dir):
            if f.endswith('.py') and not f == '__init__.py':
                existing_migration_files.append(f)
        existing_migration_files.sort()
        return existing_migration_files

    def get_last_migration(self, existing_migration_files):
        if existing_migration_files:
            return existing_migration_files[-1]

    def get_content_from_migration_file(self, migration_file):
        if migration_file:
            content = importlib.import_module(migration_file.split('.')[0])
            return (content.old_state, content.actions, content.new_state)
        return ({}, {}, {})

    def create_migrations(self):
        timestamp = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
        existing_migration_files = self.get_existing_migration_files()
        last_migration_number = len(existing_migration_files)
        last_migration = self.get_last_migration(existing_migration_files)
        _, _, new_state = self.get_content_from_migration_file(last_migration)
        old_state = new_state

        migration_file_path = os.path.join(
            self.migration_dir, str(last_migration_number + 1).zfill(3) + '_' + timestamp + '.py'
        )

        actions = self.render_actions(old_state, self.current_model_state)
        if not actions:
            print("No changes detected")
            return

        if actions.get('creations'):
            print("Creations: {0}".format(', '.join(actions.get('creations').keys())))

        if actions.get('deletions'):
            print("Deletions: {0}".format(', '.join(actions.get('deletions').keys())))

        if actions.get('fields_to_add'):
            print("Fields to add: {0}".format(', '.join(actions.get('fields_to_add').keys())))

        if actions.get('fields_to_remove'):
            print("Fields to remove: {0}".format(', '.join(actions.get('fields_to_remove').keys())))

        with open(migration_file_path, 'w') as migration_file:
            old_state_string = "old_state = " + pformat(old_state) + "\n\n"
            actions_string = "actions = " + pformat(actions) + "\n\n"
            new_state_string = "new_state = " + pformat(self.current_model_state) + "\n\n"
            content = old_state_string + actions_string + new_state_string
            migration_file.write(content)

    def get_dummy(self, attrs):
        dummy = DbObject
        setattr(dummy, 'tablename', attrs['tablename'])
        setattr(dummy, 'fieldnames', [])
        for field in attrs['fields']:
            for fieldname, field_conf in field.items():
                dummy.fieldnames.append(fieldname)
                field_attrs = field_conf['field_attrs']
                if field_attrs.get('reference_class'):
                    ref_cls = field_attrs.get('reference_class')
                    field_attrs['reference_class'] = self.ref_models[ref_cls]
                field_cls = field_dict.get(field_conf.get('field_type'))
                field_inst = field_cls(**field_attrs)
                setattr(field_inst, 'adaptor', self.adaptor)
                setattr(field_inst, 'fieldname', fieldname)
                setattr(dummy, fieldname, field_inst)
        return dummy

    def create_table(self, attrs):
        migration_dummy = self.get_dummy(attrs)
        migration_dummy.create_table()

    def drop_table(self, attrs):
        migration_dummy = self.get_dummy(attrs)
        migration_dummy.drop_table()

    def add_fields(self, model, fields, old_state):
        attrs = old_state[model]
        migration_dummy = self.get_dummy(attrs)
        for field in fields:
            field_type = field_dict[list(field.values())[0]['field_type']]
            field_attrs = list(field.values())[0]['field_attrs']
            field_dummy = field_type(**field_attrs)
            field_dummy.fieldname = list(field.keys())[0]
            field_dummy.adaptor = self.adaptor
            migration_dummy.add_field(field_dummy)

    def drop_fields(self, model, fields, old_state):
        attrs = old_state[model]
        migration_dummy = self.get_dummy(attrs)
        for field in fields:
            field_type = field_dict[list(field.values())[0]['field_type']]
            field_attrs = list(field.values())[0]['field_attrs']
            field_dummy = field_type(**field_attrs)
            field_dummy.fieldname = list(field.keys())[0]
            field_dummy.adaptor = self.adaptor
            migration_dummy.drop_field(field_dummy, migration_dummy)
        pass

    def run_migrations(self):
        existing_migration_files = self.get_existing_migration_files()
        done_migrations = [name[1] for name in self.adaptor.get_done_migrations()[0]]
        migrations_to_run = [f for f in existing_migration_files if f not in done_migrations]
        if not migrations_to_run:
            print("Nothing to migrate")
        for migration_file in migrations_to_run:
            print("Running migration: %s" % migration_file)
            old_state, actions, new_state = self.get_content_from_migration_file(migration_file)

            for creation in actions.get('creations', {}).items():
                self.create_table(creation[1])
            for deletion in actions.get('deletions', {}).items():
                self.drop_table(deletion[1])

            for field_creation in actions.get('fields_to_add', {}).items():
                self.add_fields(field_creation[0], field_creation[1], old_state)

            for field_deleteion in actions.get('fields_to_remove', {}).items():
                self.drop_fields(field_deleteion[0], field_deleteion[1], old_state)

            self.adaptor.insert_migration(migration_file)
