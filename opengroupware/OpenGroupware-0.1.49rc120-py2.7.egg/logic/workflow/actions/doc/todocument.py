#
# Copyright (c) 2012, 2013, 2014, 2015, 2016
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
from coils.core import CoilsException, get_yaml_struct_from_project7000
from coils.core.logic import ActionCommand


def retrieved_aliased_property_index(context):

    prop_map = get_yaml_struct_from_project7000(
        context, '/PropertyAliases.yaml',
    )
    if not prop_map:
        return dict()
    return prop_map


class MessageToDocumentAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "message-to-document"
    __aliases__ = ['messageToDocument', 'messageToDocumentAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):

        if self._project_id.isdigit():
            project = self._ctx.run_command(
                'project::get', id=long(self._project_id)
            )
        else:
            project = self._ctx.run_command(
                'project::get', number=self._project_id,
            )

        if not project:
            raise CoilsException(
                'Unable to marshall project identified as "{0}"'.
                format(self._project_id, )
            )

        folder = self._ctx.run_command(
            'project::get-path',
            path=self._filepath,
            project=project,
            create=True,
        )

        document = self._ctx.run_command(
            'folder::ls', id=folder.object_id, name=self._filename,
        )
        if document:
            '''
            A document at this path already exists, so we are updating it
            This will create a new revision of the document, provided the
            storage backend supports document versioning
            '''
            document = document[0]
            self._ctx.run_command(
                'document::set',
                object=document,
                values={},
                handle=self.rfile,
            )
        else:
            document = self._ctx.run_command(
                'document::new',
                name=self._filename,
                values={},
                project=project,
                folder=folder,
                handle=self.rfile,
            )
        # Update the abstract of the document
        document.abstract = self._abstract

        self._ctx.property_manager.set_property(
            entity=document,
            namespace='http://www.opengroupware.us/mswebdav',
            attribute='contentType',
            value=self.input_message.mimetype,
        )

        self._ctx.property_manager.set_property(
            entity=document,
            namespace='http://www.opengroupware.us/mswebdav',
            attribute='isTransient',
            value='NO',
        )

        """
        Process XATTRs onto the new document
        """
        self.log_message(
            '{0} property alias values specified'
            .format(len(self._pa_values), ),
            category='debug'
        )
        if self._pa_values:
            alias_map = retrieved_aliased_property_index(self._ctx)
            if not alias_map:
                self.log.warn('No Property Alias Map found')
            for key, value in self._pa_values.items():
                if key in alias_map:
                    self._ctx.property_manager.set_property(
                        entity=document,
                        namespace=alias_map[key]['namespace'],
                        attribute=alias_map[key]['attribute'],
                        value=value,
                    )
                    self.log_message(
                        'Stored value from property alias "{0}" to object '
                        'property {{{1}}}{2}'
                        .format(
                            key,
                            alias_map[key]['namespace'],
                            alias_map[key]['attribute'],
                        ),
                        category='debug'
                    )
                else:
                    self.log_message(
                        'Property alias for key "{0}" does not resolve '
                        'provided value has been discarded'
                        .format(key, ),
                        category='info'
                    )

        """
        if the process has a process-task then link the document to the task.
        """
        if self.process.task_id:
            task = self._ctx.run_command(
                'task::get', id=self.process.task_id,
            )
            if task:
                self._ctx.link_manager.link(
                    task, document, label=self._filename,
                )

        """
        Additional meta-data
        """
        self._ctx.property_manager.set_property(
            entity=document,
            namespace='http://www.opengroupware.us/oie',
            attribute='sourceMessageLabel',
            value=self.input_message.label,
        )

        self._ctx.property_manager.set_property(
            entity=document,
            namespace='http://www.opengroupware.us/oie',
            attribute='sourceProcessid',
            value=self.process.object_id,
        )

        if self.process.route:
            self._ctx.property_manager.set_property(
                entity=document,
                namespace='http://www.opengroupware.us/oie',
                attribute='sourceRouteId',
                value=self.process.route.object_id,
            )
            self._ctx.property_manager.set_property(
                entity=document,
                namespace='http://www.opengroupware.us/oie',
                attribute='sourceRouteName',
                value=self.process.route.name,
            )

        self._ctx.audit_at_commit(
            object_id=document.object_id,
            action='10_commented',
            message=(
                'Document created from message by OGo#{0} [Process]'
                .format(self.process.object_id, )
            ),
            version=document.version,
        )

        self.wfile.write(unicode(document.object_id))

    def parse_action_parameters(self):

        self._project_id = self.action_parameters.get('projectId', None, )
        if not self._project_id:
            raise CoilsException('No project specified for document save')
        self._project_id = self.process_label_substitutions(self._project_id)

        self._filepath = self.process_label_substitutions(
            self.action_parameters.get('filePath', '/')
        )
        self._filepath = self._filepath.strip()
        if (len(self._filepath) > 1) and (self._filepath.endswith('/')):
            self._filepath = self._filepath[:-1]

        self._filename = self.process_label_substitutions(
            self.action_parameters.get('filename', 'noname.data')
        )

        self._abstract = self.process_label_substitutions(
            self.action_parameters.get('abstract', self._filename)
        )

        #
        # Take XATTR values out of action parameters
        #
        self._pa_values = dict()
        for key, value, in self.action_parameters.items():
            if not key.startswith('pa_'):
                continue
            self._pa_values[key[3:]] = self.process_label_substitutions(
                value
            )

    def do_epilogue(self):
        pass
