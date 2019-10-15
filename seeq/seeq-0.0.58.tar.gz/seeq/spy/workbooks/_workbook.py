import copy
import glob
import io
import json
import os
import re
import requests
import sys

from bs4 import BeautifulSoup

from ...base import gconfig
from .. import _common
from .. import _login
from .._common import DependencyNotFound

from seeq.base import system, util
from seeq.sdk43 import *
from seeq.sdk43.rest import ApiException


class ItemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            return o.definition
        else:
            return o


class Item:
    def __init__(self, definition=None, *, original_item_map=None, status=None):
        self.definition = definition if definition else dict()

        if original_item_map is not None:
            original_item_map[self.id] = Item.get_original_id(self)

    def __contains__(self, key):
        return _common.present(self.definition, key)

    def __getitem__(self, key):
        return _common.get(self.definition, key)

    def __setitem__(self, key, val):
        self.definition[key] = val

    def __repr__(self):
        return '%s "%s" (%s)' % (self.type, self.name, self.id)

    @property
    def id(self):
        return _common.get(self.definition, 'ID')

    @property
    def name(self):
        return _common.get(self.definition, 'Name')

    @property
    def type(self):
        return _common.get(self.definition, 'Type')

    @staticmethod
    def _dict_from_id(item_id):
        items_api = ItemsApi(_login.client)
        item_output = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1

        def _parse(val):
            if val == 'true':
                return True
            elif val == 'false':
                return False
            else:
                return val

        definition = {prop.name: _parse(prop.value) for prop in item_output.properties}
        definition['Name'] = item_output.name
        definition['Type'] = item_output.type

        if 'UIConfig' in definition:
            definition['UIConfig'] = json.loads(definition['UIConfig'])

        # For some reason, these are coming back as lower case, which makes things inconsistent
        if 'Scoped To' in definition and isinstance(definition['Scoped To'], str):
            definition['Scoped To'] = definition['Scoped To'].upper()

        if item_output.ancillaries:
            definition['Ancillaries'] = list()
            for item_ancillary_output in item_output.ancillaries:  # type: ItemAncillaryOutputV1
                item_ancillary_dict = Item._dict_via_attribute_map(item_ancillary_output, {
                    'data_id': 'Data ID',
                    'datasource_class': 'Datasource Class',
                    'datasource_id': 'Datasource ID',
                    'description': 'Description',
                    'id': 'ID',
                    'name': 'Name',
                    'scoped_to': 'Scoped To',
                    'type': 'Type'
                })

                if item_ancillary_output.items:
                    item_ancillary_dict['Items'] = list()
                    for ancillary_item_output in item_ancillary_output.items:  # type: AncillaryItemOutputV1
                        ancillary_item_dict = Item._dict_via_attribute_map(ancillary_item_output, {
                            'id': 'ID',
                            'name': 'Name',
                            'order': 'Order',
                            'type': 'Type'
                        })
                        item_ancillary_dict['Items'].append(ancillary_item_dict)

                definition['Ancillaries'].append(item_ancillary_dict)

        return definition

    @staticmethod
    def _dict_via_attribute_map(item, attribute_map):
        d = dict()
        for attr, prop in attribute_map.items():
            if hasattr(item, attr):
                d[prop] = getattr(item, attr)

        return d

    @staticmethod
    def _dict_from_scalar_value_output(scalar_value_output):
        """
        :type scalar_value_output: ScalarValueOutputV1
        """
        d = dict()
        d['Value'] = scalar_value_output.value
        d['Unit Of Measure'] = scalar_value_output.uom
        return d

    @staticmethod
    def _str_from_scalar_value_dict(scalar_value_dict):
        if isinstance(scalar_value_dict['Value'], str):
            return '%s' % scalar_value_dict['Value']
        elif isinstance(scalar_value_dict['Value'], int):
            return '%d %s' % (scalar_value_dict['Value'], scalar_value_dict['Unit Of Measure'])
        else:
            return '%f %s' % (scalar_value_dict['Value'], scalar_value_dict['Unit Of Measure'])

    @staticmethod
    def _property_input_from_scalar_str(scalar_str):
        match = re.match(r'([+\-\d.]+)(.*)', scalar_str)
        if not match:
            return None

        uom = match.group(2) if match.group(2) else None
        return PropertyInputV1(unit_of_measure=uom, value=float(match.group(1)))

    @staticmethod
    def _property_output_from_item_output(item_output, property_name):
        props = [p for p in item_output.properties if p.name == property_name]
        return props[0] if len(props) == 1 else None

    @staticmethod
    def formula_string_from_list(formula_list):
        return '\n'.join(formula_list) if isinstance(formula_list, list) else str(formula_list)

    @staticmethod
    def formula_list_from_string(formula_string):
        return formula_string.split('\n') if '\n' in formula_string else formula_string

    @staticmethod
    def data_id_from_item_id(label, item_id):
        return '[%s] %s' % (label, item_id)

    @staticmethod
    def item_id_from_data_id(data_id, item_id):
        regex = r'\[(.*?)\] (%s)' % _common.GUID_REGEX
        match = re.fullmatch(regex, data_id)
        return (match.group(2) if match else item_id).upper()

    @staticmethod
    def replace_guids(document, item_map):
        if document is None:
            return

        matches = re.finditer(_common.GUID_REGEX, document, flags=re.IGNORECASE)
        new_report = document
        for match in matches:
            if match.group(0).upper() in item_map:
                new_report = re.sub(match.group(0), item_map[match.group(0).upper()], new_report, flags=re.IGNORECASE)

        return new_report

    def use_original_ids(self, original_item_map):
        if _common.get(self.definition, 'Datasource Class') != _common.DEFAULT_DATASOURCE_CLASS or \
                _common.get(self.definition, 'Datasource ID') != _common.DEFAULT_DATASOURCE_ID:
            return

        self.definition = json.loads(Item.replace_guids(json.dumps(self.definition), original_item_map))

        del self.definition['Datasource Class']
        del self.definition['Datasource ID']
        del self.definition['Data ID']

    @staticmethod
    def get_original_id(item):
        if _common.get(item, 'Datasource Class') != _common.DEFAULT_DATASOURCE_CLASS or \
                _common.get(item, 'Datasource ID') != _common.DEFAULT_DATASOURCE_ID or \
                _common.get(item, 'Data ID') is None:
            return item['ID'].upper()

        return Item.item_id_from_data_id(item['Data ID'], item['ID'])

    @staticmethod
    def pull(item_id, *, original_item_map=None, allowed_types=None, status=None):
        definition = Item._dict_from_id(item_id)
        if allowed_types and definition['Type'] not in allowed_types:
            return None
        if original_item_map is None:
            original_item_map = dict()
        derived_class = getattr(sys.modules[__name__], definition['Type'])
        item = derived_class(definition, original_item_map=original_item_map, status=status)
        item.specialize(item_id)
        original_item_map[item_id.upper()] = Item.get_original_id(item)
        return item

    def specialize(self, item_id):
        pass

    @staticmethod
    def load(definition):
        derived_class = getattr(sys.modules[__name__], definition['Type'])
        return derived_class(definition)

    def _specialize_formula_based_item(self, calculated_item):
        self.definition['Formula'] = Item.formula_list_from_string(self.definition['Formula'])
        self.definition['Formula Parameters'] = dict()
        for parameter in calculated_item.parameters:  # type: FormulaParameterOutputV1
            if parameter.item:
                self.definition['Formula Parameters'][parameter.name] = parameter.item.id
            else:
                self.definition['Formula Parameters'][parameter.name] = parameter.formula

    def scrape_auth_datasources(self):
        return set()


class ItemWithOwnerAndAcl(Item):
    def decide_owner(self, owner_id, datasource_maps, item_map, *, use_original_owner=False):
        users_api = UsersApi(_login.client)
        user_output = users_api.get_me()  # type: UserOutputV1

        if owner_id is not None:
            if owner_id != user_output.id and not user_output.is_admin:
                raise RuntimeError('Logged in user must be an admin if owner_id is not themselves')

            return owner_id

        if use_original_owner:
            if not user_output.is_admin:
                raise RuntimeError('Logged in user must be an admin if use_original_owner=True')

            owner_item = Workbook.find_identity(self['Owner'], datasource_maps=datasource_maps, item_map=item_map)
            owner_id = owner_item.id
        else:
            owner_id = user_output.id

        return owner_id

    def _pull_owner_and_acl(self, owner_id):
        items_api = ItemsApi(_login.client)

        self['Owner'] = User.pull(owner_id).definition

        acl_output = items_api.get_access_control(id=self['ID'])  # type: AclOutputV1
        access_control = list()
        for ace_output in acl_output.acl:  # type: AceOutputV1
            ace_dict = Item._dict_via_attribute_map(ace_output, {
                'access_level': 'Access Level',
                'created_at': 'Created At',
                'id': 'ID'
            })

            if ace_output.identity.type == 'User':
                identity = User.pull(ace_output.identity.id)
            else:
                identity = UserGroup.pull(ace_output.identity.id)

            ace_dict['Identity'] = identity.definition
            access_control.append(ace_dict)

        self.definition['Access Control'] = access_control

    def _push_acl(self, pushed_id, datasource_maps, item_map, *, replace, strict):
        if 'Access Control' not in self:
            return

        items_api = ItemsApi(_login.client)
        acl_output = items_api.get_access_control(id=pushed_id)  # type: AclOutputV1
        for acl_to_push in self['Access Control']:
            found = False

            try:
                identity = Workbook.find_identity(acl_to_push['Identity'], datasource_maps, item_map)
            except _common.DependencyNotFound:
                if strict:
                    raise

                continue

            for existing_acl in acl_output.acl:  # type: AceOutputV1
                if existing_acl.access_level != acl_to_push['Access Level']:
                    continue

                if existing_acl.identity.id != identity.id:
                    continue

                found = True
                setattr(existing_acl, 'used', True)
                break

            if found:
                continue

            items_api.add_access_control_entry(id=pushed_id,
                                               body=AceInputV1(access_level=acl_to_push['Access Level'],
                                                               identity_id=identity.id))

        if replace:
            for existing_acl in acl_output.acl:  # type: AceOutputV1
                if hasattr(existing_acl, 'used') and getattr(existing_acl, 'used'):
                    continue

                items_api.remove_access_control_entry(id=pushed_id, ace_id=existing_acl.id)

    def _pull_ancestors(self, ancestors):
        if ancestors is None:
            return

        self.definition['Ancestors'] = [ancestor.id for ancestor in ancestors]

    def scrape_auth_datasources(self):
        referenced_datasources = set()

        def _scrape_auth_datasource(d, key):
            if key in d and 'Datasource Class' in d[key] and 'Datasource ID' in d[key]:
                referenced_datasources.add((d[key]['Datasource Class'], d[key]['Datasource ID']))

        _scrape_auth_datasource(self, 'Owner')
        if 'Access Control' in self:
            for acl in self['Access Control']:
                _scrape_auth_datasource(acl, 'Identity')

        return referenced_datasources


class Folder(ItemWithOwnerAndAcl):
    def specialize(self, item_id):
        folders_api = FoldersApi(_login.client)
        folder_output = folders_api.get_folder(folder_id=self['ID'])  # type: FolderOutputV1
        self._pull_owner_and_acl(folder_output.owner.id)
        self._pull_ancestors(folder_output.ancestors)

    def push(self, parent_folder_id, datasource_maps, item_map, *, owner_id=None, to_original_owner=False, label=None,
             replace_acl=False):
        items_api = ItemsApi(_login.client)
        folders_api = FoldersApi(_login.client)
        folder_item = Workbook.find_item(label, self.id)

        owner_id = self.decide_owner(owner_id, datasource_maps, item_map, use_original_owner=to_original_owner)

        if folder_item:
            props = [ScalarPropertyV1(name='Name', value=self['Name'])]
            if 'Description' in self:
                props.append(ScalarPropertyV1(name='Description', value=self['Description']))

            items_api.set_properties(id=folder_item.id, body=props)
            items_api.change_owner(item_id=folder_item.id, new_owner_id=owner_id)
            if parent_folder_id is not None:
                folders_api.move_item_to_folder(folder_id=parent_folder_id, item_id=folder_item.id)

        else:
            folder_input = FolderInputV1()
            folder_input.name = self['Name']
            if 'Description' in self:
                folder_input.description = self['Description']
            folder_input.owner_id = owner_id
            folder_input.parent_folder_id = parent_folder_id

            folder_item = folders_api.create_folder(body=folder_input)

            data_id = Workbook.data_id_from_item_id(label, self.definition['ID'])
            items_api.set_properties(id=folder_item.id, body=[
                ScalarPropertyV1(name='Datasource Class', value=_common.DEFAULT_DATASOURCE_CLASS),
                ScalarPropertyV1(name='Datasource ID', value=_common.DEFAULT_DATASOURCE_ID),
                ScalarPropertyV1(name='Data ID', value=data_id)])

        if replace_acl:
            self._push_acl(folder_item.id, datasource_maps, item_map, replace=True, strict=False)

        return folder_item.id


class Workbook(ItemWithOwnerAndAcl):
    def __init__(self, definition=None, *, original_item_map=None, status=None):
        super().__init__(definition, original_item_map=original_item_map)

        self.item_inventory = dict()
        self.status = status

        if definition is not None and 'ID' in definition:
            self._pull(definition['ID'], original_item_map)

    def update_status(self, result, count_increment):
        if self.status is None:
            return

        status_df, timer, quiet = self.status
        status_df.loc[status_df['ID'] == self.id, 'Count'] = \
            status_df.loc[status_df['ID'] == self.id, 'Count'] + count_increment
        status_df.loc[status_df['ID'] == self.id, 'Time'] = _common.timer_elapsed(timer)
        status_df.loc[status_df['ID'] == self.id, 'Result'] = result

        if len(status_df) <= 20:
            display_df = status_df
        else:
            display_df = status_df[~status_df['Result'].isin(['Queued', 'Success'])]

        _common.display_status('[%d/%d] Processing %s "%s"' %
                               (len(status_df[status_df['Result'] != 'Queued']),
                                len(status_df), self['Workbook Type'], self['Name']),
                               _common.STATUS_RUNNING, quiet, display_df)

    def _pull(self, workbook_id, original_item_map):
        workbooks_api = WorkbooksApi(_login.client)
        workbook_output = workbooks_api.get_workbook(id=workbook_id)  # type: WorkbookOutputV1

        self.definition['Path'] = ' >> '.join([a.name for a in workbook_output.ancestors])
        self.definition['Workbook Type'] = _common.get_workbook_type(workbook_output.data)

        self._pull_owner_and_acl(workbook_output.owner.id)
        self._pull_ancestors(workbook_output.ancestors)

        self.update_status('Pulling workbook', 1)

        self.definition['Data'] = json.loads(workbook_output.data)
        self.definition['workbookState'] = json.loads(self.definition['workbookState'])

        self.worksheets = list()
        worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_id)  # type: WorksheetOutputListV1
        for worksheet_output in worksheet_output_list.worksheets:  # type: WorksheetOutputV1
            self.update_status('Pulling worksheets', 1)
            self.worksheets.append(Worksheet(self, Item._dict_from_id(worksheet_output.id),
                                             original_item_map=original_item_map,
                                             worksheet_output=worksheet_output))

        self._scrape_item_inventory(original_item_map)
        self._scrape_datasource_inventory()
        self._construct_default_datasource_maps()

    def use_original_ids(self, original_item_map):
        super().use_original_ids(original_item_map)

        for worksheet in self.worksheets:
            worksheet.use_original_ids(original_item_map)

        new_inventory = dict()
        for item_id, item in self.item_inventory.items():
            item.use_original_ids(original_item_map)
            new_inventory[item['ID']] = item

        self.item_inventory = new_inventory

    def pull_worksteps(self, workstep_tuples):
        for workbook_id, worksheet_id, workstep_id in workstep_tuples:
            if workbook_id != self.id:
                continue

            worksheets = [worksheet for worksheet in self.worksheets if worksheet.id == worksheet_id]
            if len(worksheets) == 0:
                continue

            worksheets[0].pull_worksteps([workstep_id])

    def push(self, *, owner_id=None, to_original_owner=False, folder_id=None, item_map=None, label=None,
             replace_acl=False, status=None):
        self.status = status

        workbook_item = Workbook.find_item(label, self.id)

        owner_id = self.decide_owner(owner_id, self.datasource_maps, item_map, use_original_owner=to_original_owner)

        workbooks_api = WorkbooksApi(_login.client)
        items_api = ItemsApi(_login.client)
        datasources_api = DatasourcesApi(_login.client)
        folders_api = FoldersApi(_login.client)

        datasource_input = _common.get_data_lab_datasource_input()
        datasources_api.create_datasource(body=datasource_input)

        props = list()
        if not workbook_item:
            workbook_input = WorkbookInputV1()
            workbook_input.name = self.definition['Name']
            workbook_input.description = _common.get(self.definition, 'Description')
            workbook_input.folder_id = folder_id
            workbook_input.owner_id = owner_id
            workbook_input.data = json.dumps(self.definition['Data'])
            workbook_output = workbooks_api.create_workbook(body=workbook_input)  # type: WorkbookOutputV1

            data_id = Workbook.data_id_from_item_id(label, self.id)
            items_api.set_properties(id=workbook_output.id, body=[
                ScalarPropertyV1(name='Datasource Class', value=_common.DEFAULT_DATASOURCE_CLASS),
                ScalarPropertyV1(name='Datasource ID', value=_common.DEFAULT_DATASOURCE_ID),
                ScalarPropertyV1(name='Data ID', value=data_id)])

            workbook_id = workbook_output.id
        else:
            workbook_id = workbook_item.id
            # If the workbook happens to be archived, un-archive it. If you're pushing a new copy it seems likely
            # you're intending to revive it.
            items_api.set_properties(id=workbook_item.id, body=[ScalarPropertyV1(name='Archived', value=False)])

            if folder_id is not None:
                folders_api.move_item_to_folder(folder_id=folder_id, item_id=workbook_id)

        if item_map is None:
            item_map = dict()

        item_map[self.id.upper()] = workbook_id.upper()

        if replace_acl:
            self._push_acl(workbook_id, self.datasource_maps, item_map, replace=True, strict=False)

        remaining_inventory = dict(self.item_inventory)
        while len(remaining_inventory) > 0:
            at_least_one_thing_pushed = False
            dependencies_not_found = list()
            dict_iterator = dict(remaining_inventory)
            for item_id, item in dict_iterator.items():
                if item['Type'] in ['Folder']:
                    at_least_one_thing_pushed = True
                    del remaining_inventory[item_id]
                    continue

                try:
                    self.update_status('Pushing item inventory', 1)
                    item_output = item.push(self.datasource_maps, workbook_id=workbook_id, item_map=item_map,
                                            label=label)
                    item_map[item_id.upper()] = item_output.id.upper()
                    at_least_one_thing_pushed = True
                    del remaining_inventory[item_id]
                except DependencyNotFound as e:
                    self.update_status('Pushing item inventory', -1)
                    dependencies_not_found.append(e.identifier)

            if not at_least_one_thing_pushed:
                raise RuntimeError('Could not resolve the following dependencies:\n%s\n'
                                   'Therefore, could not import the following items:\n%s\n' %
                                   ('\n'.join(dependencies_not_found),
                                    '\n'.join(remaining_inventory.keys())))

        props.append(ScalarPropertyV1(name='Name', value=self.definition['Name']))
        if _common.present(self.definition, 'Description'):
            props.append(ScalarPropertyV1(name='Description', value=self.definition['Description']))
        if _common.present(self.definition, 'Data'):
            props.append(ScalarPropertyV1(name='Data', value=json.dumps(self.definition['Data'])))
        if _common.present(self.definition, 'workbookState'):
            props.append(ScalarPropertyV1(name='workbookState', value=json.dumps(self.definition['workbookState'])))

        items_api.set_properties(id=workbook_id, body=props)

        for worksheet in self.worksheets:
            self.update_status('Pushing worksheet', 1)
            worksheet.push(workbook_id, item_map, label=label)

        return item_map

    def push_containing_folders(self, item_map, use_full_path, parent_folder_id, to_original_owner, replace_acl):
        if 'Ancestors' not in self:
            return parent_folder_id

        create_folders_now = False
        if use_full_path or 'Search Folder ID' not in self:
            create_folders_now = True

        for ancestor_id in self['Ancestors']:
            if create_folders_now:
                folder = self.item_inventory[ancestor_id]  # type: Folder
                parent_folder_id = folder.push(parent_folder_id, self.datasource_maps, item_map,
                                               to_original_owner=to_original_owner, replace_acl=replace_acl)
            elif self['Search Folder ID'] == ancestor_id:
                create_folders_now = True

        return parent_folder_id

    @staticmethod
    def find_identity(identity_dict, datasource_maps, item_map):
        if identity_dict['ID'] in item_map:
            return item_map[identity_dict['ID']]

        if identity_dict['Type'] == 'User':
            identity = User(identity_dict)
        else:
            identity = UserGroup(identity_dict)

        identity_item = identity.push(datasource_maps=datasource_maps, item_map=item_map)

        item_map[identity_item.id] = identity_item
        return identity_item

    @staticmethod
    def find_item(label, item_id, workbook_id=None):
        """
        :rtype: ItemSearchPreviewV1
        """
        items_api = ItemsApi(_login.client)

        if not label:
            try:
                item_output = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1
                return item_output
            except ApiException:
                # Fall through to looking via Data ID
                pass

        data_id = Workbook.data_id_from_item_id(label, item_id)
        _filters = [
            'Datasource Class==%s && Datasource ID==%s && Data ID==%s' % (
                _common.DEFAULT_DATASOURCE_CLASS, _common.DEFAULT_DATASOURCE_ID, data_id),
            '@includeUnsearchable']

        if workbook_id:
            search_results = items_api.search_items(
                filters=_filters,
                scope=workbook_id,
                offset=0,
                limit=2)  # type: ItemSearchPreviewPaginatedListV1
        else:
            search_results = items_api.search_items(
                filters=_filters,
                offset=0,
                limit=2)  # type: ItemSearchPreviewPaginatedListV1

        if len(search_results.items) == 0:
            return None

        if len(search_results.items) > 1:
            raise RuntimeError('Multiple workbook/worksheet/workstep items found with Data ID of "%s"', data_id)

        return search_results.items[0]

    @property
    def referenced_items(self):
        referenced_items = list()
        for worksheet in self.worksheets:
            referenced_items.extend(worksheet.referenced_items)

        referenced_items.extend(self.scoped_items)

        return referenced_items

    @property
    def referenced_workbooks(self):
        references = dict()
        for worksheet in self.worksheets:
            for (workbook_id, worksheet_id, workstep_id) in worksheet.referenced_worksteps:
                if workbook_id not in references:
                    references[workbook_id] = set()

                references[workbook_id].add((workbook_id, worksheet_id, workstep_id))

        return references

    def _get_default_workbook_folder(self):
        return os.path.join(os.getcwd(), 'Workbook_%s' % self.id)

    @staticmethod
    def _get_workbook_json_file(workbook_folder):
        return os.path.join(workbook_folder, 'Workbook.json')

    @staticmethod
    def _get_items_json_file(workbook_folder):
        return os.path.join(workbook_folder, 'Items.json')

    @staticmethod
    def _get_datasources_json_file(workbook_folder):
        return os.path.join(workbook_folder, 'Datasources.json')

    @staticmethod
    def _get_datasource_map_json_file(workbook_folder, datasource_map):
        return os.path.join(
            workbook_folder, system.cleanse_filename(
                'Datasource_Map_%s_%s_%s.json' % (datasource_map['Datasource Class'],
                                                  datasource_map['Datasource ID'],
                                                  datasource_map['Datasource Name'])))

    def save(self, workbook_folder=None):
        if not workbook_folder:
            workbook_folder = self._get_default_workbook_folder()

        if os.path.exists(workbook_folder):
            system.removetree(workbook_folder, keep_top_folder=True)

        os.makedirs(workbook_folder, exist_ok=True)

        workbook_json_file = Workbook._get_workbook_json_file(workbook_folder)

        definition_dict = dict(self.definition)
        definition_dict['Worksheets'] = list()
        for worksheet in self.worksheets:
            worksheet.save(workbook_folder)
            definition_dict['Worksheets'].append(worksheet.id)

        with open(workbook_json_file, 'w', encoding='utf-8') as f:
            json.dump(definition_dict, f, indent=4)

        items_json_file = Workbook._get_items_json_file(workbook_folder)
        with open(items_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.item_inventory, f, indent=4, sort_keys=True, cls=ItemJSONEncoder)

        datasources_json_file = Workbook._get_datasources_json_file(workbook_folder)
        with open(datasources_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.datasource_inventory, f, indent=4, sort_keys=True, cls=ItemJSONEncoder)

        for datasource_map in self.datasource_maps:
            datasource_map_file = Workbook._get_datasource_map_json_file(workbook_folder, datasource_map)
            with open(datasource_map_file, 'w', encoding='utf-8') as f:
                json.dump(datasource_map, f, indent=4)

    def _load(self, workbook_folder):
        if not os.path.exists(workbook_folder):
            raise RuntimeError('Workbook folder "%s" does not exist' % workbook_folder)

        workbook_json_file = Workbook._get_workbook_json_file(workbook_folder)
        if not os.path.exists(workbook_json_file):
            raise RuntimeError('Workbook JSON file "%s" does not exist' % workbook_json_file)

        with open(workbook_json_file, 'r', encoding='utf-8') as f:
            self.definition = json.load(f)

        self.worksheets = list()
        for worksheet_id in self.definition['Worksheets']:
            self.worksheets.append(Worksheet.load_from_workbook_folder(self, workbook_folder, worksheet_id))

        del self.definition['Worksheets']

        self.item_inventory = Workbook._load_inventory(Workbook._get_items_json_file(workbook_folder))
        self.datasource_inventory = Workbook._load_inventory(Workbook._get_datasources_json_file(workbook_folder))
        self.datasource_maps = Workbook.load_datasource_maps(workbook_folder)

    @staticmethod
    def load_datasource_maps(folder):
        datasource_map_files = glob.glob(os.path.join(folder, 'Datasource_Map_*.json'))
        datasource_maps = list()
        for datasource_map_file in datasource_map_files:
            with open(datasource_map_file, 'r', encoding='utf-8') as f:
                datasource_maps.append(json.load(f))

        return datasource_maps

    @staticmethod
    def _load_inventory(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            loaded_inventory = json.load(f)

        inventory_dict = dict()
        for item_id, item in loaded_inventory.items():
            inventory_dict[item_id] = Item.load(item)

        return inventory_dict

    @staticmethod
    def load(workbook_folder):
        workbook = Workbook()
        workbook._load(workbook_folder)
        return workbook

    def _scrape_datasource_inventory(self):
        referenced_datasources = self.scrape_auth_datasources()
        for _id, item in self.item_inventory.items():
            referenced_datasources.update(item.scrape_auth_datasources())
            if 'Datasource Class' in item and 'Datasource ID' in item:
                referenced_datasources.add((item['Datasource Class'], item['Datasource ID']))

        self.datasource_inventory = dict()
        for datasource_class, datasource_id in referenced_datasources:
            datasource = Datasource.from_datasource_id(datasource_class, datasource_id)
            self.datasource_inventory[datasource.id] = datasource

        return self.datasource_inventory

    def _construct_default_datasource_maps(self):
        self.datasource_maps = list()
        for _id, datasource in self.datasource_inventory.items():
            datasource_map = {
                'Datasource Class': datasource['Datasource Class'],
                'Datasource ID': datasource['Datasource ID'],
                'Datasource Name': datasource['Name'],
                'Tag-Level Map Files': list(),
                'RegEx-Based Maps': [
                    {
                        'Old': {
                            'Type': r'(?<type>.*)',
                            'Datasource Class': datasource['Datasource Class'],
                            'Datasource Name': datasource['Name']
                        },
                        'New': {
                            'Type': '${type}',
                            'Datasource Class': datasource['Datasource Class'],
                            'Datasource Name': datasource['Name']
                        }
                    }
                ]
            }

            if datasource['Datasource Class'] in ['Auth', 'Windows Auth', 'LDAP', 'OAuth 2.0']:
                datasource_map['RegEx-Based Maps'].append(copy.deepcopy(datasource_map['RegEx-Based Maps'][0]))

                datasource_map['RegEx-Based Maps'][0]['Old']['Type'] = 'User'
                datasource_map['RegEx-Based Maps'][0]['Old']['Username'] = r'(?<username>.*)'
                datasource_map['RegEx-Based Maps'][0]['New']['Type'] = 'User'
                datasource_map['RegEx-Based Maps'][0]['New']['Username'] = '${username}'

                datasource_map['RegEx-Based Maps'][1]['Old']['Type'] = 'UserGroup'
                datasource_map['RegEx-Based Maps'][1]['Old']['Name'] = r'(?<name>.*)'
                datasource_map['RegEx-Based Maps'][1]['New']['Type'] = 'UserGroup'
                datasource_map['RegEx-Based Maps'][1]['New']['Name'] = '${name}'
            else:
                datasource_map['RegEx-Based Maps'][0]['Old']['Data ID'] = r'(?<data_id>.*)'
                datasource_map['RegEx-Based Maps'][0]['New']['Data ID'] = '${data_id}'

            self.datasource_maps.append(datasource_map)

    def _scrape_item_inventory(self, original_item_map):
        self._scrape_references_from_scope()

        self.item_inventory = dict()

        if 'Ancestors' in self:
            for ancestor_id in self['Ancestors']:
                self.update_status('Scraping folders', 0)

                try:
                    item = Item.pull(ancestor_id, original_item_map=original_item_map, allowed_types=['Folder'])
                except ApiException as e:
                    if e.status == 404:
                        continue

                    raise

                if item is None:
                    continue

                self.update_status('Scraping folders', 1)

                self.item_inventory[ancestor_id] = item

        for reference in self.referenced_items:
            if reference.id in self.item_inventory:
                continue

            allowed_types = [
                'StoredSignal',
                'CalculatedSignal',
                'StoredCondition',
                'CalculatedCondition',
                'CalculatedScalar',
                'Chart',
                'ThresholdMetric'
            ]

            self.update_status('Scraping item inventory', 0)

            try:
                item = Item.pull(reference.id, original_item_map=original_item_map, allowed_types=allowed_types)
            except ApiException as e:
                if e.status == 404:
                    continue

                raise

            if item is None:
                continue

            if 'Is Generated' in item and item['Is Generated']:
                continue

            self.update_status('Scraping item inventory', 1)

            self.item_inventory[reference.id] = item

            dependencies = self._scrape_references_from_dependencies(reference.id)

            for dependency in dependencies:
                if dependency.id in self.item_inventory:
                    continue

                self.update_status('Scraping item dependency', 0)

                try:
                    dep_item = Item.pull(dependency.id, original_item_map=original_item_map,
                                         allowed_types=allowed_types)
                except ApiException as e:
                    if e.status == 404:
                        continue

                    raise

                if dep_item is None:
                    continue

                if 'Is Generated' in dep_item and dep_item['Is Generated']:
                    continue

                self.update_status('Scraping item dependency', 1)

                self.item_inventory[dependency.id] = dep_item

    def _scrape_references_from_scope(self):
        items_api = ItemsApi(_login.client)

        self.update_status('Scraping scope references', 0)

        self.scoped_items = list()
        offset = 0
        while True:
            search_results = items_api.search_items(
                filters=['', '@excludeGloballyScoped'],
                scope=self.id,
                offset=offset,
                limit=_common.DEFAULT_SEARCH_PAGE_SIZE,
            )  # type: ItemSearchPreviewPaginatedListV1

            self.scoped_items.extend([Reference(item.id, Reference.SCOPED) for item in search_results.items])

            if len(search_results.items) < search_results.limit:
                break

            offset += search_results.limit

        return self.scoped_items

    def _scrape_references_from_dependencies(self, item_id):
        items_api = ItemsApi(_login.client)
        referenced_items = list()

        self.update_status('Scraping dependencies', 0)

        try:
            dependencies = items_api.get_formula_dependencies(id=item_id)  # type: ItemDependencyOutputV1
        except ApiException as e:
            if e.status == 404:
                # For some reason, the item_id is unknown. We've seen this at Exxon, so just skip it.
                return referenced_items

            raise

        for dependency in dependencies.dependencies:  # type: ItemParameterOfOutputV1
            referenced_items.append(Reference(
                dependency.id,
                Reference.DEPENDENCY
            ))

        return referenced_items


class Worksheet(Item):
    def __init__(self, workbook, definition=None, *, original_item_map=None, worksheet_output=None):
        super().__init__(definition, original_item_map=original_item_map)

        self.workbook = workbook

        if definition is not None and 'ID' in definition:
            self._pull(definition['ID'], worksheet_output)

    def _pull(self, worksheet_id, worksheet_output):
        if worksheet_output is None:
            workbooks_api = WorkbooksApi(_login.client)
            worksheet_output = workbooks_api.get_worksheet(
                workbook_id=self.workbook.id, worksheet_id=worksheet_id)  # type: WorksheetOutputV1

        if self.workbook['Workbook Type'] == 'Analysis':
            self.document = Journal(self)
        else:
            self.document = Report(self)

        self.document.pull()

        current_workstep_id = Worksheet._get_current_workstep_id(worksheet_output.workstep)

        workstep_ids_to_pull = list()
        if current_workstep_id is not None:
            workstep_ids_to_pull.append(current_workstep_id)
            self.definition['Current Workstep ID'] = current_workstep_id

        for workbook_id, worksheet_id, workstep_id in self.document.referenced_worksteps:
            if worksheet_id == self.id:
                workstep_ids_to_pull.extend([workstep_id])

        self.worksteps = dict()
        self.pull_worksteps(workstep_ids_to_pull)

    def use_original_ids(self, original_item_map):
        super().use_original_ids(original_item_map)

        self.document.use_original_ids(original_item_map)

        for _, workstep in self.worksteps.items():
            workstep.use_original_ids(original_item_map)

    def pull_worksteps(self, workstep_ids):
        for workstep_id in workstep_ids:
            if workstep_id not in self.worksteps:
                self.worksteps[workstep_id] = Workstep(self, {'ID': workstep_id})

    def push(self, workbook_id, item_map, label=None):
        worksheet_item = Workbook.find_item(label, self.id)

        workbooks_api = WorkbooksApi(_login.client)
        items_api = ItemsApi(_login.client)
        props = list()
        if not worksheet_item:
            worksheet_input = WorksheetInputV1()
            worksheet_input.name = self.definition['Name']
            worksheet_output = workbooks_api.create_worksheet(
                workbook_id=workbook_id, body=worksheet_input)  # type: WorksheetOutputV1

            data_id = Workbook.data_id_from_item_id(label, self.id)
            items_api.set_properties(id=worksheet_output.id, body=[
                ScalarPropertyV1(name='Datasource Class', value=_common.DEFAULT_DATASOURCE_CLASS),
                ScalarPropertyV1(name='Datasource ID', value=_common.DEFAULT_DATASOURCE_ID),
                ScalarPropertyV1(name='Data ID', value=data_id)])

            worksheet_id = worksheet_output.id
        else:
            worksheet_id = worksheet_item.id
            props.append(ScalarPropertyV1(name='Name', value=self.definition['Name']))
            items_api.set_properties(id=worksheet_item.id, body=props)

        item_map[self.id.upper()] = worksheet_id.upper()

        for workstep_id, workstep in self.worksteps.items():
            pushed_workstep_id = workstep.push_to_specific_worksheet(workbook_id, worksheet_id, item_map)
            item_map[workstep_id.upper()] = pushed_workstep_id.upper()

            if workstep_id == self.definition['Current Workstep ID']:
                workbooks_api.set_current_workstep(workbook_id=workbook_id,
                                                   worksheet_id=worksheet_id,
                                                   workstep_id=pushed_workstep_id)

        self.document.push(workbook_id, worksheet_id, item_map)

    @property
    def referenced_items(self):
        referenced_items = list()
        for workstep_id, workstep in self.worksteps.items():  # type: Workstep
            referenced_items.extend(workstep.referenced_items)

        referenced_items.extend(self.document.referenced_items)

        return referenced_items

    @property
    def referenced_worksteps(self):
        return self.document.referenced_worksteps

    @staticmethod
    def _get_current_workstep_id(workstep):
        if not workstep:
            return None

        return workstep.split('/')[-1]

    @staticmethod
    def _get_worksheet_json_file(workbook_folder, worksheet_id):
        return os.path.join(workbook_folder, 'Worksheet_%s.json' % worksheet_id)

    def save(self, workbook_folder):
        worksheet_json_file = Worksheet._get_worksheet_json_file(workbook_folder, self.id)

        with open(worksheet_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.definition, f, indent=4)

        self.document.save(workbook_folder)

        for workstep_id, workstep in self.worksteps.items():
            workstep.save(workbook_folder)

    def _load(self, workbook_folder, worksheet_id):
        worksheet_json_file = Worksheet._get_worksheet_json_file(workbook_folder, worksheet_id)

        with open(worksheet_json_file, 'r', encoding='utf-8') as f:
            self.definition = json.load(f)

        if self.workbook['Workbook Type'] == 'Analysis':
            self.document = Journal.load(self, workbook_folder)
        else:
            self.document = Report.load(self, workbook_folder)

        self.worksteps = dict()
        workstep_files = glob.glob(os.path.join(workbook_folder, 'Worksheet_%s_Workstep_*.json' % worksheet_id))
        for workstep_file in workstep_files:
            match = re.match(r'.*?Worksheet_.*?_Workstep_(.*?).json$', workstep_file)
            workstep_id = match.group(1)
            self.worksteps[workstep_id] = Workstep.load_from_workbook_folder(self, workbook_folder, workstep_id)

    @staticmethod
    def load_from_workbook_folder(workbook, workbook_folder, worksheet_id):
        worksheet = Worksheet(workbook)
        worksheet._load(workbook_folder, worksheet_id)
        return worksheet


class Annotation:
    def __init__(self, worksheet, annotation_type):
        """
        :type worksheet: Worksheet
        """
        self.annotation_type = annotation_type
        self.worksheet = worksheet
        self.html = None  # str
        self.images = dict()

    def _find_image_references(self):
        if not self.html:
            return list()

        matches = re.finditer(r'src="/api(/annotations/(.*?)/images/(.*?))"', self.html)
        return [(match.group(1), match.group(2), match.group(3)) for match in matches]

    @property
    def referenced_items(self):
        return list()

    @property
    def referenced_worksteps(self):
        return self._find_workstep_references()

    def _find_workstep_references(self):
        return set()

    def pull(self):
        self.images = dict()
        annotations_api = AnnotationsApi(_login.client)
        annotations = annotations_api.get_annotations(
            annotates=[self.worksheet.id])  # type: AnnotationListOutputV1

        for annotation_item in annotations.items:  # type: AnnotationOutputV1
            annotation_output = annotations_api.get_annotation(id=annotation_item.id)  # AnnotationOutputV1
            if annotation_output.type != self.annotation_type:
                continue

            self.html = annotation_output.document

            image_references = self._find_image_references()
            for query_params, annotation_id, image_id in image_references:
                if (annotation_id, image_id) in self.images:
                    continue

                self.worksheet.workbook.update_status('Pulling image', 1)

                api_client_url = gconfig.get_api_url()
                request_url = api_client_url + query_params
                response = requests.get(request_url, headers={
                    "Accept": "application/vnd.seeq.v1+json",
                    "x-sq-auth": _login.client.auth_token
                }, verify=Configuration().verify_ssl)

                self.images[(annotation_id, image_id)] = response.content

    def use_original_ids(self, original_item_map):
        self.html = Item.replace_guids(self.html, original_item_map)

    def push(self, workbook_id, worksheet_id, item_map):
        annotations_api = AnnotationsApi(_login.client)

        annotations = annotations_api.get_annotations(
            annotates=[worksheet_id])  # type: AnnotationListOutputV1

        if self.html is None:
            self.html = ''

        doc = Item.replace_guids(self.html, item_map)

        bs = BeautifulSoup(doc, features='html.parser')
        find_result = bs.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title'])
        name = 'Unnamed'
        description = None

        if len(find_result) > 0:
            name = ' '.join(re.split(r'[\s\n]+', find_result[0].get_text().strip())[:20])
        if len(find_result) > 1:
            description = ' '.join(re.split(r'[\s\n]+', find_result[1].get_text().strip())[:50])

        new_annotation = AnnotationInputV1()
        new_annotation.document = ''
        new_annotation.name = name if len(name.strip()) > 0 else 'Unnamed'
        new_annotation.description = description
        new_annotation.type = self.annotation_type

        relevant_annotations = [a for a in annotations.items if a.type == self.annotation_type]
        if len(relevant_annotations) == 0:
            new_annotation.interests = [
                AnnotationInterestInputV1(interest_id=workbook_id),
                AnnotationInterestInputV1(interest_id=worksheet_id)
            ]

            relevant_annotation = annotations_api.create_annotation(body=new_annotation)  # type: AnnotationOutputV1
        else:
            relevant_annotation = relevant_annotations[0]

        for query_params, annotation_id, image_id in self._find_image_references():
            api_client_url = gconfig.get_api_url()
            request_url = api_client_url + '/annotations/%s/images' % relevant_annotation.id

            self.worksheet.workbook.update_status('Pushing image', 1)

            response = requests.post(url=request_url,
                                     files={
                                         "file": (image_id, io.BytesIO(self.images[(annotation_id, image_id)]))
                                     },
                                     headers={
                                         "Accept": "application/vnd.seeq.v1+json",
                                         "x-sq-auth": _login.client.auth_token
                                     },
                                     verify=Configuration().verify_ssl)

            if response.status_code != 201:
                raise RuntimeError('Could not upload image file %s for worksheet %d' % (image_id, worksheet_id))

            link_json = json.loads(response.content)

            doc = doc.replace('src="/api/annotations/%s/images/%s"' % (annotation_id, image_id),
                              'src="%s"' % link_json['link'])

        new_annotation.document = doc
        new_annotation.interests = list()
        for interest in relevant_annotation.interests:  # type: AnnotationInterestOutputV1
            interest_item = interest.item  # type: ItemPreviewV1
            # At Chevron, we encountered a case where there were multiple interests returned with the same ID, which
            # caused Appserver to choke when updating the annotation. So filter those out.
            if any(interest_item.id == i.interest_id for i in new_annotation.interests):
                continue
            new_interest = AnnotationInterestInputV1()
            new_interest.interest_id = interest_item.id
            new_interest.detail_id = interest.capsule
            new_annotation.interests.append(new_interest)
        new_annotation.created_by_id = relevant_annotation.created_by.id

        annotations_api.update_annotation(
            id=relevant_annotation.id, body=new_annotation)  # type: AnnotationOutputV1

    def _get_annotation_html_file(self, workbook_folder):
        return os.path.join(workbook_folder, '%s_%s.html' % (self.annotation_type, self.worksheet.id))

    @staticmethod
    def _get_image_file(workbook_folder, image_id_tuple):
        return os.path.join(workbook_folder, 'Image_%s_%s' % image_id_tuple)

    @staticmethod
    def _get_html_attr(fragment, attribute):
        attr_match = re.findall(r'\s+%s="(.*?)"' % attribute, fragment)
        return attr_match[0] if len(attr_match) > 0 else None

    @staticmethod
    def _check_map(_id, item_map):
        if _id not in item_map:
            raise DependencyNotFound(_id)

        return _id

    def save(self, workbook_folder):
        journal_html_file = self._get_annotation_html_file(workbook_folder)
        with open(journal_html_file, 'w', encoding='utf-8') as f:
            if self.html:
                prettified_html = BeautifulSoup(self.html, features='html.parser').prettify()
                # If we don't trim the spaces within <a> tags, you'll get extra spaces underlined in the UI
                prettified_html = re.sub(r'(<a .*?>)[\s\n]+(.*?)[\s\n]+(</a>)', r'\1\2\3', prettified_html)
                f.write(prettified_html)

        for image_id_tuple, content in self.images.items():
            image_file = Journal._get_image_file(workbook_folder, image_id_tuple)
            with open(image_file, 'wb') as f:
                f.write(content)

    def _load(self, workbook_folder):
        journal_html_file = self._get_annotation_html_file(workbook_folder)

        with open(journal_html_file, 'r', encoding='utf-8') as f:
            self.html = f.read()

        matches = re.finditer(r'src="/api(/annotations/(.*?)/images/(.*?))"', self.html)
        for match in matches:
            image_id_tuple = (match.group(2), match.group(3))
            image_file = Journal._get_image_file(workbook_folder, image_id_tuple)

            with open(image_file, 'rb') as f:
                self.images[image_id_tuple] = f.read()


class Journal(Annotation):
    def __init__(self, worksheet):
        super().__init__(worksheet, 'Journal')

    @staticmethod
    def load(worksheet, workbook_folder):
        journal = Journal(worksheet)
        journal._load(workbook_folder)
        return journal

    @property
    def referenced_items(self):
        referenced_items = list()
        if self.html:
            matches = re.finditer(r'item&#61;(%s)' % _common.GUID_REGEX, self.html, re.IGNORECASE)
            for match in matches:
                referenced_items.append(Reference(match.group(1).upper(), Reference.JOURNAL, self.worksheet))

        return referenced_items

    def _find_workstep_references(self):
        if not self.html:
            return set()

        workstep_references = set()
        regex = r'workbook&#61;(%s)&amp;worksheet&#61;(%s)&amp;workstep&#61;(%s)' % (
            _common.GUID_REGEX, _common.GUID_REGEX, _common.GUID_REGEX)
        matches = re.finditer(regex, self.html, re.IGNORECASE)

        for match in matches:
            workstep_references.add((match.group(1).upper(), match.group(2).upper(), match.group(3).upper()))

        return workstep_references


class Report(Annotation):
    def __init__(self, worksheet):
        super().__init__(worksheet, 'Report')

    @staticmethod
    def load(worksheet, workbook_folder):
        report = Report(worksheet)
        report._load(workbook_folder)
        return report

    def _find_workstep_references(self):
        if not self.html:
            return set()

        workstep_references = set()
        link_matches = re.finditer(r'<a .*?</a>', self.html, re.IGNORECASE)
        for link_match in link_matches:
            link_html = link_match.group(0)
            href_regex = r'.*href="\/view\/worksheet\/(%s)\/(%s)\?workstepId(&#61;|=)(%s).*?".*' % (
                _common.GUID_REGEX, _common.GUID_REGEX, _common.GUID_REGEX)
            href_match = re.match(href_regex, link_html)
            if href_match:
                workstep_references.add((href_match.group(1), href_match.group(2), href_match.group(4)))

        img_matches = re.finditer(r'<img .*?>', self.html, re.IGNORECASE)
        for img_match in img_matches:
            img_html = img_match.group(0)
            data_seeq_workbookid = Annotation._get_html_attr(img_html, 'data-seeq-workbookid')
            data_seeq_worksheetid = Annotation._get_html_attr(img_html, 'data-seeq-worksheetid')
            data_seeq_workstepid = Annotation._get_html_attr(img_html, 'data-seeq-workstepid')
            if data_seeq_workbookid and data_seeq_worksheetid and data_seeq_workstepid:
                workstep_references.add((data_seeq_workbookid, data_seeq_worksheetid, data_seeq_workstepid))

        return workstep_references


class Reference:
    JOURNAL = 'Journal'
    DETAILS = 'Details'
    SCOPED = 'Scoped'
    DEPENDENCY = 'Dependency'
    EMBEDDED_CONTENT = 'Embedded Content'

    def __init__(self, _id, _provenance, worksheet=None):
        """
        :type _id: str
        :type _provenance: str
        :type worksheet: Worksheet
        """
        self.id = _id
        self.provenance = _provenance
        self.worksheet = worksheet

    def __repr__(self):
        if self.worksheet is not None:
            return '%s reference on "%s" (%s)' % (self.provenance, self.worksheet.name, self.id)
        else:
            return '%s (%s)' % (self.provenance, self.id)


class Workstep(Item):
    def __init__(self, worksheet, definition=None, original_item_map=None):
        super().__init__(definition, original_item_map=original_item_map)

        self.worksheet = worksheet

        if definition is not None and 'ID' in definition:
            self._pull(definition['ID'])

    def _pull(self, workstep_id):
        workbooks_api = WorkbooksApi(_login.client)
        workstep_output = workbooks_api.get_workstep(workbook_id=self.worksheet.workbook.id,
                                                     worksheet_id=self.worksheet.id,
                                                     workstep_id=workstep_id)  # type: WorkstepOutputV1

        self.definition['Data'] = json.loads(workstep_output.data)

        self.referenced_items = self._scrape_referenced_items()

    def use_original_ids(self, original_item_map):
        self.definition['Data'] = json.loads(Item.replace_guids(json.dumps(self.data), original_item_map))

    def push_to_specific_worksheet(self, workbook_id, worksheet_id, item_map):
        workbooks_api = WorkbooksApi(_login.client)

        workstep_input = WorkstepInputV1()
        workstep_input.data = Item.replace_guids(json.dumps(self.data), item_map)

        workstep_output = workbooks_api.create_workstep(
            workbook_id=workbook_id, worksheet_id=worksheet_id, body=workstep_input)  # type: WorkstepOutputV1

        item_map[self.id.upper()] = workstep_output.id.upper()

        return workstep_output.id

    @property
    def data(self):
        return _common.get(self.definition, 'Data', default=dict())

    def _scrape_referenced_items(self):
        referenced_items = list()

        matches = re.finditer(_common.GUID_REGEX, json.dumps(self.data), re.IGNORECASE)

        for match in matches:
            referenced_items.append(Reference(match.group(0).upper(), Reference.DETAILS, self.worksheet))

        return referenced_items

    @staticmethod
    def _get_workstep_json_file(workbook_folder, worksheet_id, workstep_id):
        return os.path.join(workbook_folder, 'Worksheet_%s_Workstep_%s.json' % (worksheet_id, workstep_id))

    def save(self, workbook_folder):
        workstep_json_file = Workstep._get_workstep_json_file(workbook_folder, self.worksheet.id, self.id)
        with open(workstep_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.definition, f, indent=4)

    def _load(self, workbook_folder, workstep_id):
        workstep_json_file = Workstep._get_workstep_json_file(workbook_folder, self.worksheet.id, workstep_id)

        with open(workstep_json_file, 'r', encoding='utf-8') as f:
            self.definition = json.load(f)

    @staticmethod
    def load_from_workbook_folder(worksheet, workbook_folder, workstep_id):
        workstep = Workstep(worksheet)
        workstep._load(workbook_folder, workstep_id)
        return workstep


class Datasource(Item):
    @staticmethod
    def from_datasource_id(datasource_class, datasource_id):
        _filters = ['Datasource Class==' + datasource_class,
                    'Datasource ID==' + datasource_id]

        filters_arg = [' && '.join(_filters), '@includeUnsearchable']

        items_api = ItemsApi(_login.client)
        item_search_list = items_api.search_items(
            types=['Datasource'],
            filters=filters_arg,
            limit=1)  # type: ItemSearchPreviewPaginatedListV1

        if len(item_search_list.items) != 1:
            raise RuntimeError(
                'Datasource Class "%s" and Datasource ID "%s" not found' % (datasource_class, datasource_id))

        return Item.pull(item_search_list.items[0].id, original_item_map=dict())


class TableDatasource(Datasource):
    pass


class StoredOrCalculatedItem(Item):
    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        raise RuntimeError('Pushed called but StoredOrCalculatedItem.push() not overloaded')

    def push_ancillaries(self, pushed_item, workbook_id):
        if 'Ancillaries' not in self:
            return

        items_api = ItemsApi(_login.client)
        if not isinstance(pushed_item, ItemOutputV1):
            pushed_item = items_api.get_item_and_all_properties(id=pushed_item.id)  # type: ItemOutputV1

        ancillaries_api = AncillariesApi(_login.client)

        ancillary_input = AncillaryInputV1()
        ancillary_input.item_id = pushed_item.id

        ancillary_input.ancillaries = list()
        for ancillary_dict in self['Ancillaries']:
            found = False
            for item_ancillary_output in pushed_item.ancillaries:  # type: ItemAncillaryOutputV1
                if 'Scoped To' in ancillary_dict and ancillary_dict['Scoped To'] is not None and \
                        ancillary_dict['Scoped To'] != workbook_id:
                    continue
        ancillary_item_input = AncillaryItemInputV1(

        )

        ancillaries_api.create_ancillary()
        ancillaries_api.update_ancillary()


class StoredItem(StoredOrCalculatedItem):
    SEARCHABLE_PROPS = ['Datasource Class', 'Datasource ID', 'Datasource Name', 'Data ID',
                        'Type', 'Name', 'Description', 'Username']

    @staticmethod
    def _execute_regex_map(old_definition, regex_map):
        capture_groups = dict()
        for prop, regex in regex_map['Old'].items():
            if prop not in StoredItem.SEARCHABLE_PROPS:
                raise RuntimeError('Datasource map contains an unsearchable property "%s". Searchable properties:\n%s',
                                   '\n'.join(StoredItem.SEARCHABLE_PROPS))

            if prop not in old_definition:
                return None

            regex = util.pythonize_regex_capture_group_names(regex)
            match = re.match(regex, old_definition[prop])
            if not match:
                return None

            capture_groups.update(match.groupdict())

        new_definition = dict()
        for prop, regex in regex_map['New'].items():
            new_definition[prop] = util.replace_tokens_in_regex(regex, capture_groups, escape=False)

        return new_definition

    @staticmethod
    def _find_datasource_name(datasource_class, datasource_id, datasource_maps):
        for datasource_map in datasource_maps:
            if datasource_map['Datasource Class'] == datasource_class and \
                    datasource_map['Datasource ID'] == datasource_id:
                return datasource_map['Datasource Name']

        raise RuntimeError('Could not find Datasource Class "%s" and Datasource ID "%s" in datasource maps' %
                           (datasource_class, datasource_id))

    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        items_api = ItemsApi(_login.client)

        logging = list()
        try:
            item = items_api.get_item_and_all_properties(id=self.id)  # type: ItemOutputV1
        except ApiException:
            item = None
            logging.append('ID %s not found directly' % self.id)

        for i in range(0, len(datasource_maps)):
            if item is not None:
                break

            datasource_map = datasource_maps[i]
            if 'RegEx-Based Maps' in datasource_map:
                new_definition = None
                for regex_map in datasource_map['RegEx-Based Maps']:
                    old_definition = dict(self.definition)
                    if 'Datasource Class' in old_definition and 'Datasource ID' in old_definition:
                        old_definition['Datasource Name'] = \
                            StoredItem._find_datasource_name(old_definition['Datasource Class'],
                                                             old_definition['Datasource ID'],
                                                             datasource_maps)

                    new_definition = StoredItem._execute_regex_map(old_definition, regex_map)
                    if new_definition is not None:
                        break

                if new_definition is None:
                    logging.append('RegEx-Based Map %d did not match %s for "Old" values' % (i, self))
                    continue

                if 'Datasource Name' in new_definition:
                    if 'Datasource ID' not in new_definition:
                        if 'Datasource Class' not in new_definition:
                            raise RuntimeError('"Datasource Class" required with "Datasource Name" in map:\n%s' %
                                               json.dumps(new_definition))

                        datasource_results = items_api.search_items(
                            filters=['Datasource Class==%s&&Name==%s' % (new_definition['Datasource Class'],
                                                                         new_definition['Datasource Name']),
                                     '@includeUnsearchable'],
                            types=['Datasource'],
                            limit=2)  # type: ItemSearchPreviewPaginatedListV1

                        if len(datasource_results.items) > 1:
                            raise _common.DependencyNotFound(
                                new_definition['Datasource Name'],
                                'Multiple datasources found that match "%s"' % new_definition['Datasource Name'])
                        elif len(datasource_results.items) == 0:
                            raise _common.DependencyNotFound(
                                new_definition['Datasource Name'],
                                'No datasource found that matches "%s"' % new_definition['Datasource Name'])

                        new_datasource = datasource_results.items[0]  # type: ItemSearchPreviewV1
                        new_definition['Datasource ID'] = items_api.get_property(
                            id=new_datasource.id, property_name='Datasource ID').value
                    del new_definition['Datasource Name']

                if new_definition['Type'] not in ['User', 'UserGroup']:
                    filters = ' && '.join(
                        '%s~=/^%s$/' % (prop, re.escape(val)) for prop, val in new_definition.items())
                    search_results = items_api.search_items(filters=[filters, '@includeUnsearchable'],
                                                            limit=2)  # type: ItemSearchPreviewPaginatedListV1
                    if len(search_results.items) == 0:
                        logging.append('RegEx-Based Map %d did not match %s filters:\n%s' % (i, self, filters))
                    elif len(search_results.items) > 1:
                        logging.append('RegEx-Based Map %d multiple matches %s filters:\n%s' % (i, self, filters))
                    else:
                        item = items_api.get_item_and_all_properties(
                            id=search_results.items[0].id)  # type:  ItemOutputV1
                else:
                    if new_definition['Type'] == 'User':
                        try:
                            users_api = UsersApi(_login.client)
                            item = users_api.get_user_from_username(
                                auth_datasource_class=new_definition['Datasource Class'],
                                auth_datasource_id=new_definition['Datasource ID'],
                                username=new_definition['Username'])  # type: UserOutputV1
                        except ApiException:
                            # Fall through, item not found
                            pass
                    else:
                        user_groups_api = UserGroupsApi(_login.client)
                        user_groups = user_groups_api.get_user_groups()  # type: ItemPreviewListV1
                        for user_group in user_groups.items:  # type: ItemPreviewV1
                            if user_group.name == new_definition['Name']:
                                item = user_group
                                break

        if item is None:
            raise _common.DependencyNotFound(
                self.id, 'No match for item with ID %s:\n%s' % (self.id, '\n'.join(logging)))

        if item.type in ['User', 'UserGroup']:
            return item

        datasource_id_prop = Item._property_output_from_item_output(item, 'Datasource ID')

        if item.type == 'StoredSignal' and datasource_id_prop.value != 'Example Data':
            push_override_max_interp = None

            if 'Override Maximum Interpolation' in self:
                push_override_max_interp = Item._property_input_from_scalar_str(self['Override Maximum Interpolation'])
            elif 'Maximum Interpolation' in self:
                max_interp = Item._property_input_from_scalar_str(self['Maximum Interpolation'])
                if 'Source Maximum Interpolation' in self:
                    source_max_interp = Item._property_input_from_scalar_str(self['Source Maximum Interpolation'])
                    if source_max_interp.unit_of_measure != max_interp.unit_of_measure or \
                            source_max_interp.value != max_interp.value:
                        push_override_max_interp = max_interp
                elif max_interp.unit_of_measure != 'h' or max_interp.value != 40:
                    # Before we had the override mechanism, Maximum Interpolation was edited directly. If it's different
                    # than the default of 40h, assume it was overridden.
                    push_override_max_interp = max_interp

            if push_override_max_interp is not None:
                current_max_interp = Item._property_input_from_scalar_str(
                    Item._property_output_from_item_output(item, 'Maximum Interpolation').value)

                if current_max_interp.unit_of_measure != push_override_max_interp.unit_of_measure or \
                        current_max_interp.value != push_override_max_interp.value:
                    items_api.set_property(id=item.id,
                                           property_name='Override Maximum Interpolation',
                                           body=push_override_max_interp)

        self.push_ancillaries(item, workbook_id)

        return item


class CalculatedItem(StoredOrCalculatedItem):
    pass


class StoredSignal(StoredItem):
    pass


class CalculatedSignal(CalculatedItem):
    def specialize(self, item_id):
        signals_api = SignalsApi(_login.client)
        signal_output = signals_api.get_signal(id=item_id)  # type: SignalOutputV1
        self._specialize_formula_based_item(signal_output)

    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        signals_api = SignalsApi(_login.client)
        items_api = ItemsApi(_login.client)

        data_id = Workbook.data_id_from_item_id(label, self.definition['ID'])

        signal_input = SignalInputV1()
        signal_input.name = self.definition['Name']
        if 'Description' in self.definition:
            signal_input.description = self.definition['Description']
        signal_input.formula = Item.formula_string_from_list(self.definition['Formula'])

        signal_input.formula_parameters = list()
        for parameter_name, parameter_id in self.definition['Formula Parameters'].items():
            if parameter_id not in item_map:
                raise DependencyNotFound(parameter_id)

            signal_input.formula_parameters.append('%s=%s' % (parameter_name, item_map[parameter_id.upper()]))

        if 'Number Format' in self.definition:
            signal_input.number_format = self.definition['Number Format']

        signal_input.scoped_to = workbook_id

        signal_output = signals_api.put_signal_by_data_id(datasource_class=_common.DEFAULT_DATASOURCE_CLASS,
                                                          datasource_id=_common.DEFAULT_DATASOURCE_ID,
                                                          data_id=data_id,
                                                          body=signal_input)  # type: SignalOutputV1

        if 'UIConfig' in self.definition:
            items_api.set_property(id=signal_output.id,
                                   property_name='UIConfig',
                                   body=PropertyInputV1(value=json.dumps(self.definition['UIConfig'])))

        return signal_output


class StoredCondition(StoredItem):
    pass


class CalculatedCondition(CalculatedItem):
    def specialize(self, item_id):
        conditions_api = ConditionsApi(_login.client)
        condition_output = conditions_api.get_condition(id=item_id)  # type: ConditionOutputV1
        self._specialize_formula_based_item(condition_output)

    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        conditions_api = ConditionsApi(_login.client)

        data_id = Workbook.data_id_from_item_id(label, self.definition['ID'])

        condition_input = ConditionInputV1()
        condition_input.name = self.definition['Name']
        if 'Description' in self.definition:
            condition_input.description = self.definition['Description']
        condition_input.formula = Item.formula_string_from_list(self.definition['Formula'])

        condition_input.parameters = list()
        for parameter_name, parameter_id in self.definition['Formula Parameters'].items():
            if parameter_id not in item_map:
                raise DependencyNotFound(parameter_id)

            condition_input.parameters.append('%s=%s' % (parameter_name, item_map[parameter_id.upper()]))

        if 'Number Format' in self.definition:
            condition_input.number_format = self.definition['Number Format']

        condition_input.additional_properties = list()
        if 'UIConfig' in self.definition:
            condition_input.additional_properties.append(
                ScalarPropertyV1(name='UIConfig', value=json.dumps(self.definition['UIConfig'])))

        condition_input.scoped_to = workbook_id

        condition_input.datasource_class = _common.DEFAULT_DATASOURCE_CLASS
        condition_input.datasource_id = _common.DEFAULT_DATASOURCE_ID
        condition_input.data_id = data_id

        item_batch_output = conditions_api.put_conditions(
            body=ConditionBatchInputV1(conditions=[condition_input]))  # type: ItemBatchOutputV1

        item_update_output = item_batch_output.item_updates[0]  # type: ItemUpdateOutputV1
        if item_update_output.error_message is not None:
            raise RuntimeError('Could not push condition "%s": %s' %
                               (self.definition['Name'], item_update_output.error_message))

        return item_update_output.item


class CalculatedScalar(CalculatedItem):
    def specialize(self, item_id):
        scalars_api = ScalarsApi(_login.client)
        calculated_item_output = scalars_api.get_scalar(id=item_id)  # type: CalculatedItemOutputV1
        self._specialize_formula_based_item(calculated_item_output)

    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        scalars_api = ScalarsApi(_login.client)

        data_id = Workbook.data_id_from_item_id(label, self.definition['ID'])

        scalar_input = ScalarInputV1()
        scalar_input.name = self.definition['Name']
        if 'Description' in self.definition:
            scalar_input.description = self.definition['Description']
        scalar_input.formula = Item.formula_string_from_list(self.definition['Formula'])

        scalar_input.parameters = list()
        for parameter_name, parameter_id in self.definition['Formula Parameters'].items():
            if parameter_id not in item_map:
                raise DependencyNotFound(parameter_id)

            scalar_input.parameters.append('%s=%s' % (parameter_name, item_map[parameter_id.upper()]))

        if 'Number Format' in self.definition:
            scalar_input.number_format = self.definition['Number Format']

        scalar_input.additional_properties = list()
        if 'UIConfig' in self.definition:
            scalar_input.additional_properties.append(
                ScalarPropertyV1(name='UIConfig', value=json.dumps(self.definition['UIConfig'])))

        scalar_input.scoped_to = workbook_id

        scalar_input.data_id = data_id

        item_batch_output = scalars_api.put_scalars(
            body=PutScalarsInputV1(datasource_class=_common.DEFAULT_DATASOURCE_CLASS,
                                   datasource_id=_common.DEFAULT_DATASOURCE_ID,
                                   scalars=[scalar_input]))  # type: ItemBatchOutputV1

        item_update_output = item_batch_output.item_updates[0]  # type: ItemUpdateOutputV1
        if item_update_output.error_message is not None:
            raise RuntimeError('Could not push scalar "%s": %s' %
                               (self.definition['Name'], item_update_output.error_message))

        return item_update_output.item


class Chart(CalculatedItem):
    def specialize(self, item_id):
        formulas_api = FormulasApi(_login.client)
        calculated_item_output = formulas_api.get_function(id=item_id)  # type: CalculatedItemOutputV1

        self._specialize_formula_based_item(calculated_item_output)

        if 'FormulaParameters' in self.definition:
            # Charts have these superfluous properties
            del self.definition['FormulaParameters']

    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        formulas_api = FormulasApi(_login.client)
        items_api = ItemsApi(_login.client)

        data_id = Workbook.data_id_from_item_id(label, self.definition['ID'])
        item = Workbook.find_item(label, self.definition['ID'], workbook_id)

        function_input = FunctionInputV1()
        function_input.name = self.definition['Name']
        function_input.type = self.definition['Type']
        function_input.formula = Item.formula_string_from_list(self.definition['Formula'])
        function_input.parameters = list()
        for parameter_name, parameter_id in self.definition['Formula Parameters'].items():
            if _common.is_guid(parameter_id):
                if parameter_id not in item_map:
                    raise DependencyNotFound(parameter_id)

                function_input.parameters.append(FormulaParameterInputV1(name=parameter_name,
                                                                         id=item_map[parameter_id.upper()]))
            else:
                function_input.parameters.append(FormulaParameterInputV1(name=parameter_name,
                                                                         formula=parameter_id,
                                                                         unbound=True))

        if 'Description' in self.definition:
            function_input.description = self.definition['Description']

        function_input.scoped_to = workbook_id
        function_input.data_id = data_id

        if item is None:
            calculated_item_output = formulas_api.create_function(body=function_input)  # type: CalculatedItemOutputV1

            items_api.set_properties(
                id=calculated_item_output.id,
                body=[ScalarPropertyV1(name='Datasource Class', value=_common.DEFAULT_DATASOURCE_CLASS),
                      ScalarPropertyV1(name='Datasource ID', value=_common.DEFAULT_DATASOURCE_ID),
                      ScalarPropertyV1(name='Data ID', value=data_id)])
        else:
            calculated_item_output = formulas_api.update_function(id=item.id,
                                                                  body=function_input)  # type: CalculatedItemOutputV1

        if 'UIConfig' in self.definition:
            items_api.set_properties(
                id=calculated_item_output.id,
                body=[ScalarPropertyV1(name='UIConfig', value=json.dumps(self.definition['UIConfig']))])

        return calculated_item_output


class ThresholdMetric(CalculatedItem):
    def specialize(self, item_id):
        metrics_api = MetricsApi(_login.client)
        metric = metrics_api.get_metric(id=item_id)  # type: ThresholdMetricOutputV1

        formula_parameters = dict()
        if metric.aggregation_function is not None:
            formula_parameters['Aggregation Function'] = metric.aggregation_function
        if metric.bounding_condition is not None:
            formula_parameters['Bounding Condition'] = metric.bounding_condition.id
        if metric.bounding_condition_maximum_duration is not None:
            formula_parameters['Bounding Condition Maximum Duration'] = \
                Item._dict_from_scalar_value_output(metric.bounding_condition_maximum_duration)
        if metric.duration is not None:
            formula_parameters['Duration'] = Item._dict_from_scalar_value_output(metric.duration)
        if metric.measured_item is not None:
            formula_parameters['Measured Item'] = metric.measured_item.id
        if metric.measured_item_maximum_duration is not None:
            formula_parameters['Measured Item Maximum Duration'] = \
                Item._dict_from_scalar_value_output(metric.measured_item_maximum_duration)
        if hasattr(metric, 'number_format') and metric.number_format is not None:
            formula_parameters['Number Format'] = metric.number_format
        if metric.period is not None:
            formula_parameters['Period'] = Item._dict_from_scalar_value_output(metric.period)
        if metric.process_type is not None:
            formula_parameters['Process Type'] = metric.process_type

        def _add_thresholds(_thresholds_name, _threshold_output_list):
            formula_parameters[_thresholds_name] = list()
            for threshold in _threshold_output_list:  # type: ThresholdOutputV1
                threshold_dict = dict()
                if threshold.priority is not None:
                    priority = threshold.priority  # type: PriorityV1
                    threshold_dict['Priority'] = {
                        'Name': priority.name,
                        'Level': priority.level,
                        'Color': priority.color
                    }

                if not threshold.is_generated and threshold.item:
                    threshold_dict['Item ID'] = threshold.item.id

                if threshold.value is not None:
                    if isinstance(threshold.value, ScalarValueOutputV1):
                        threshold_dict['Value'] = Item._dict_from_scalar_value_output(threshold.value)
                    else:
                        threshold_dict['Value'] = threshold.value

                formula_parameters[_thresholds_name].append(threshold_dict)

        if metric.thresholds:
            _add_thresholds('Thresholds', metric.thresholds)

        if 'AggregationFunction' in formula_parameters:
            del self.definition['AggregationFunction']

        self.definition['Formula'] = '<ThresholdMetric>'
        self.definition['Formula Parameters'] = formula_parameters

    def push(self, datasource_maps, *, workbook_id=None, item_map=None, label=None):
        items_api = ItemsApi(_login.client)
        metrics_api = MetricsApi(_login.client)

        parameters = self['Formula Parameters']

        new_item = ThresholdMetricInputV1()
        new_item.name = self.name
        new_item.scoped_to = workbook_id

        def _add_scalar_value(_attr, _key):
            if _common.present(parameters, _key):
                setattr(new_item, _attr, Item._str_from_scalar_value_dict(parameters[_key]))

        def _add_mapped_item(_attr, _key):
            if _common.present(parameters, _key):
                if parameters[_key] not in item_map:
                    raise DependencyNotFound(parameters[_key])

                setattr(new_item, _attr, item_map[parameters[_key].upper()])

        def _add_thresholds(_list, _key):
            if not _common.present(parameters, _key):
                return

            for threshold_dict in parameters[_key]:
                threshold_value = _common.get(threshold_dict, 'Value')
                if threshold_value is not None:
                    if isinstance(threshold_value, dict):
                        _list.append('%s=%s' % (threshold_dict['Priority']['Level'],
                                                Item._str_from_scalar_value_dict(threshold_value)))
                    else:
                        _list.append('%s=%s' % (threshold_dict['Priority']['Level'], threshold_value))
                elif _common.present(threshold_dict, 'Item ID'):
                    if threshold_dict['Item ID'] not in item_map:
                        raise DependencyNotFound(threshold_dict['Item ID'])

                    _list.append('%s=%s' % (threshold_dict['Priority']['Level'],
                                            item_map[threshold_dict['Item ID'].upper()]))

        new_item.aggregation_function = _common.get(parameters, 'Aggregation Function')

        _add_mapped_item('bounding_condition', 'Bounding Condition')
        _add_scalar_value('bounding_condition_maximum_duration', 'Bounding Condition Maximum Duration')
        _add_scalar_value('duration', 'Duration')
        _add_mapped_item('measured_item', 'Measured Item')
        _add_scalar_value('measured_item_maximum_duration', 'Measured Item Maximum Duration')
        new_item.number_format = _common.get(parameters, 'Number Format')
        _add_scalar_value('period', 'Period')
        new_item.number_format = _common.get(parameters, 'Process Type')

        new_item.thresholds = list()
        _add_thresholds(new_item.thresholds, 'Thresholds')

        data_id = Workbook.data_id_from_item_id(label, self.definition['ID'])
        item = Workbook.find_item(label, self.definition['ID'], workbook_id)

        if item is None:
            threshold_metric_output = metrics_api.create_threshold_metric(
                body=new_item)  # type: ThresholdMetricOutputV1

            items_api.set_properties(
                id=threshold_metric_output.id,
                body=[ScalarPropertyV1(name='Datasource Class', value=_common.DEFAULT_DATASOURCE_CLASS),
                      ScalarPropertyV1(name='Datasource ID', value=_common.DEFAULT_DATASOURCE_ID),
                      ScalarPropertyV1(name='Data ID', value=data_id)])
        else:
            threshold_metric_output = metrics_api.put_threshold_metric(
                id=item.id,
                body=new_item)  # type: ThresholdMetricOutputV1

        if 'UIConfig' in self.definition:
            items_api.set_properties(
                id=threshold_metric_output.id,
                body=[ScalarPropertyV1(name='UIConfig', value=json.dumps(self.definition['UIConfig']))])

        return threshold_metric_output


class Identity(StoredItem):
    def pull_datasource(self, identity):
        # noinspection PyBroadException
        try:
            if identity.type == 'User':
                auth_api = AuthApi(_login.client)
                auth_providers_output = auth_api.get_auth_providers()  # type: AuthProvidersOutputV1
                users_api = UsersApi(_login.client)
                user_output = users_api.get_user(id=identity.id)  # type: UserOutputV1

                for auth_provider in auth_providers_output.auth_providers:  # DatasourceOutputV1
                    if auth_provider.name == user_output.datasource_name:
                        self['Datasource Class'] = auth_provider.datasource_class
                        self['Datasource ID'] = auth_provider.datasource_id
                        self['Datasource Name'] = auth_provider.name
                        break
            else:
                # In .45, groups will come from different datasources. For now, hard-code it.
                # user_groups_api = UserGroupsApi(_login.client)
                # user_group_output = user_groups_api.get_user_group(id=identity.id)  # type: UserGroupOutputV1
                self['Datasource Class'] = 'Auth'
                self['Datasource ID'] = 'Seeq'
                self['Datasource Name'] = 'Seeq'
        except BaseException:
            # If we can't get extra data on the user, that's OK
            pass


class User(Identity):
    @staticmethod
    def pull(item_id, *, original_item_map=None, allowed_types=None, status=None):
        users_api = UsersApi(_login.client)
        user_output = users_api.get_user(id=item_id)  # type: UserOutputV1

        item = User({
            'ID': user_output.id,
            'Type': user_output.type,
            'Name': user_output.name,
            'Username': user_output.username,
            'First Name': user_output.first_name,
            'Last Name': user_output.last_name,
            'Email': user_output.email,
            'Is Admin': user_output.is_admin
        })

        if original_item_map is None:
            original_item_map = dict()
        item.pull_datasource(user_output)
        original_item_map[item_id.upper()] = Item.get_original_id(item)
        return item


class UserGroup(Identity):
    @staticmethod
    def pull(item_id, *, original_item_map=None, allowed_types=None, status=None):
        usergroups_api = UserGroupsApi(_login.client)
        usergroup_output = usergroups_api.get_user_group(user_group_id=item_id)  # type: UserGroupOutputV1

        item = UserGroup({
            'ID': usergroup_output.id,
            'Type': usergroup_output.type,
            'Name': usergroup_output.name
        })

        if original_item_map is None:
            original_item_map = dict()
        item.pull_datasource(usergroup_output)
        original_item_map[item_id.upper()] = Item.get_original_id(item)
        return item
