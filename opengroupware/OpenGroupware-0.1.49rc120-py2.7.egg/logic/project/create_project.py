#
# Copyright (c) 2010, 2013, 2014, 2015
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
# THE SOFTWARE
#
from datetime import datetime
from yaml.parser import ParserError
from coils.core import \
    Project, \
    CoilsException, \
    PropertyManager, \
    get_yaml_struct_from_project7000
from coils.core.logic import CreateCommand
from keymap import COILS_PROJECT_KEYMAP
from command import ProjectCommand


class CreateProject(CreateCommand, ProjectCommand):
    __domain__ = "project"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_PROJECT_KEYMAP
        self.entity = Project
        CreateCommand.prepare(self, ctx, **params)

    def _initialize_object_properties(self, target, description):
        properties = description.get('properties', {})
        for pn, pav in properties.items():
            try:
                pns, pas = PropertyManager.Parse_Property_Name(pn)
            except:
                # property name cannot be parsed
                # TODO: alert about malformed property name
                pass
            else:
                self._ctx.property_manager.set_property(
                    entity=target,
                    namespace=pns,
                    attribute=pas,
                    value=pav,
                )

    def _initialize_object_permissions(self, target, description):
        permissions = description.get('permissions', {})
        for tn, tp in permissions.items():
            team = self._ctx.run_command('team::get', name=tn, )
            if not team:
                # TODO: alert about undesolved team name
                continue
            self._ctx.run_command(
                'object::set-acl',
                object=target,
                context_id=team.object_id,
                permissions=tp,
                action='allowed',
            )
            self._ctx.audit_at_commit(
                object_id=self.obj.object_id,
                action='00_created',
                message=(
                    'Set ACL for team "{0}" on OGo#{1} granting "{2}"'
                    .format(tn, target.object_id, tp, )
                ),
            )

    def _initialize_project_folder(self, parent, description):
        folder = self._ctx.run_command(
            'folder::ls', folder=parent, name=description['name'],
        )
        if folder:
            folder = folder[0]
        if not folder:
            folder = self._ctx.run_command(
                'folder::new',
                folder=parent,
                values={'name': description['name'], },
            )
            self._ctx.audit_at_commit(
                object_id=self.obj.object_id,
                action='00_created',
                message=(
                    'Created folder "{0}" as OGo#{1}'
                    .format(description['name'], folder.object_id, )
                ),
            )

        self._initialize_object_properties(
            target=folder, description=description,
        )
        self._initialize_object_permissions(
            target=folder, description=description,
        )

        if 'children' in description:
            for child_description in description['children']:
                self._initialize_project_folder(folder, child_description, )

    def _template_project_apply(self, project, root_folder):

        if project.kind is None:
            return

        try:
            ruleset = get_yaml_struct_from_project7000(
                self._ctx,
                'Rules/Projects/{0}.yaml'.format(project.kind, ),
                access_check=False,
            )
        except ParserError as exc:
            self._ctx.log.exception(exc)
            self._ctx.log.error(
                'YAML text of project skeleton for  kind "{0}" is invalid'
                .format(project.kind, )
            )
            # TODO: alert about malformed property name
            ruleset = None
        except CoilsException as exc:
            self._ctx.log.exception(exc)
            ruleset = None
            self._ctx.log.debug(
                'No project skeleton loaded for projects of kind "{0}"'
                .format(project.kind, )
            )
            ruleset = None
        else:
            self._ctx.log.debug(
                'Project skeleton loaded for tasks of kind "{0}"'
                .format(project.kind, )
            )

        if ruleset is None:
            return

        self._initialize_object_permissions(
            target=self.obj,
            description=ruleset,
        )

        folder_tree = ruleset.get('folders', [])
        for description in folder_tree:
            self._initialize_project_folder(root_folder, description)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)

    def fill_missing_values(self):
        if (self.obj.start is None):
            self.obj.start = datetime.now()
        if (self.obj.end is None):
            self.obj.end = datetime(2032, 12, 31, 18, 59, 59)
        if (self.obj.sky_url is None):
            # TODO: This should default to something meaningful
            pass
        if (self.obj.is_fake is None):
            self.obj.is_fake = 0

    def run(self):
        CreateCommand.run(self)
        self.fill_missing_values()
        self.set_contacts()
        self.set_enterprises()
        self.set_assignment_acls()
        self.obj.status = 'inserted'
        self.save()
        if (self.obj.number is None):
            self.obj.number = 'P{0}'.format(self.obj.object_id)

        # TODO: set modified

        folder = self._ctx.run_command(
            'folder::new',
            values={
                'projectId': self.obj.object_id,
                'name': self.obj.number,
            },
        )

        self._template_project_apply(project=self.obj, root_folder=folder, )
