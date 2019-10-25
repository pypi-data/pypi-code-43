#
# Copyright (c) 2009, 2014, 2015, 2016
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
from coils.core import CoilsException
from coils.net import OmphalosCollection, DAVFolder
from processfolder import ProcessFolder
from bpmlobject import BPMLObject
from versionsfolder import VersionsFolder
from signalobject import SignalObject
from proplistobject import PropertyListObject
from workflow import WorkflowPresentation

STATIC_OBJECTS = {
    'markup.xml': BPMLObject,
    'signal': SignalObject,
    'Versions': VersionsFolder,
    'propertyList.txt': PropertyListObject,
}

UNARCHIVED_STATIC_KEYS = (
    'markup.xml', 'Versions', 'propertyList.txt', 'Archive',
)


class RouteFolder(DAVFolder, WorkflowPresentation):

    """Implements /dav/Worfklow/Routes/{routeName}."""

    def __init__(self, parent, name, **params):
        """Construct RouterFolder object."""
        DAVFolder.__init__(self, parent, name, **params)
        self.entity = params['entity']
        self.route_id = self.entity.object_id
        self.archived = bool(params.get('archived', False))

    def supports_PUT(self):
        """Indicate objects may be PUT to this target. """
        return True

    def _load_contents(self):
        """
        Load the contents of the folder.

        Load the contents of the folder, this includes processes and the
        list of defined static keys.
        """
        self.data = {}

        self.log.debug(
            'Returning enumeration of processes of route {0}.'.
            format(self.name, )
        )
        processes = self.context.run_command(
            'route::get-processes', id=self.route_id, archived=self.archived,
        )
        for process in processes:
            self.insert_child(str(process.object_id), process)

        if not self.archived:
            """
            The archived folder intentionally does not contain the static keys;
            those only exist in the route's "root" folder.
            """
            for static_key in UNARCHIVED_STATIC_KEYS:
                self.insert_child(static_key, None, )

        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        """
        Return the child object by name.

        TODO: This is long and clunky, find a better way to map name
        to responses
        """
        self.log.debug('Request for folder key {0}'.format(name))
        if (name == 'Archive'):
            return RouteFolder(self, name,
                               parameters=self.parameters,
                               entity=self.entity,
                               context=self.context,
                               archived=True,
                               request=self.request)
        elif name in STATIC_OBJECTS:
            return STATIC_OBJECTS[name](
                self, name,
                parameters=self.parameters,
                entity=self.entity,
                context=self.context,
                request=self.request,
            )
        elif (name in ('.json', '.contents', '.ls')):
            result = self.context.run_command(
                'route::get-processes', id=self.route_id,
            )
            if name == '.ls':
                rendered = False
            else:
                rendered = True
            return OmphalosCollection(
                self, name,
                detailLevel=65535,
                rendered=rendered,
                data=result,
                parameters=self.parameters,
                context=self.context,
                request=self.request,
            )
        else:
            if (self.is_loaded):
                """
                Contents of folder is already loaded, so just check for
                the process
                """
                if (self.has_child(name)):
                    process = self.get_child(name)
                else:
                    process = None
            else:
                """
                Convert the requested name to a Process Id (Process objectId)
                so we can attempt to retrieve it
                """
                try:
                    pid = long(name)
                except:
                    """
                    Issue#151: Non-numeric unknown key requires to RouteFolder
                    results in a 500 response. If the requested key is not an
                    integer than it cannot be a process id and we want
                    to fail with a nice no-such-path response
                    """
                    self.no_such_path()
                # Get the requested process from Logic/ORM
                process = self.context.run_command('process::get', id=pid, )
            if process:
                return ProcessFolder(
                    self, name,
                    parameters=self.parameters,
                    entity=process,
                    context=self.context,
                    request=self.request,
                )
        self.no_such_path()

    def do_PUT(self, request_name):
        """Implement PUT hander."""
        if self.archived:
            raise CoilsException('PUT not supported in archived context')
        payload = self.request.get_request_payload()

        if request_name in ['markup.xml', 'markup.bpml', ]:
            """Update Route Markup"""
            self.context.run_command(
                'route::set', object=self.entity, markup=payload,
            )
            self.context.commit()
            self.request.simple_response(201)
            return

        """Create a new process;  the default behavior."""
        self.log.debug(
            'Attempting to create new process from route {0}'
            .format(self.route_id, )
        )
        try:
            """Determine Process priority, default to 201"""
            priority_param = self.parameters.get('.priority', None)
            if priority_param:
                try:
                    priority = int(priority_param[0])
                except:
                    raise CoilsException(
                        'Unable to parse priority value from URL parameter, '
                        'value="{0}"'
                        .format(priority_param, )
                    )
            else:
                priority = 201

            """Determine MIME-type of input message, default to binart"""
            mimetype = self.request.headers.get(
                'Content-Type', 'application/octet-stream',
            )

            origin_label = request_name.replace('\\', '_').replace('/', '_')
            if not origin_label:
                origin_label = 'input'

            """Apply XATTRs from URL to new process"""
            xattrs = dict()
            if (len(self.parameters) > 0):
                for key, value in self.parameters.items():
                    if key.startswith('.'):
                        # Skip URL parameters beginning with a dot
                        continue
                    xattrs[key] = value

            """Create the process"""
            process = self.create_process(
                route=self.entity,
                data=payload,
                priority=priority,
                mimetype=mimetype,
                origin_label=origin_label,
                xattrs=xattrs,
            )
            if not process:
                """
                process::new can choose to not create create a new
                process due to run-control rules of the route.  In that
                case the Logic command returns NULL
                """
                self.request.simple_response(
                    202,
                    data='process creation supressed by run-control',
                    mimetype='text/plain',
                    headers={
                        'X-COILS-WORKFLOW-ALERT': 'run-control violation',
                    },
                )
                ctx.context.rollback()
                return

            self.context.commit()

            self.log.info(
                'Process {0} created via DAV PUT of "{1}" by {2}.'
                .format(
                    process.object_id,
                    request_name,
                    self.context.get_login(),
                )
            )
            message = self.get_input_message(process)

            """Request main engine start!"""
            self.start_process(process)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Failed to create process')
        paths = self.get_process_urls(process)
        self.request.simple_response(
            301,
            mimetype=message.mimetype,
            headers={
                'Location': paths['self'],
                'X-COILS-WORKFLOW-MESSAGE-UUID': message.uuid,
                'X-COILS-WORKFLOW-MESSAGE-LABEL': message.label,
                'X-COILS-WORKFLOW-PROCESS-ID': process.object_id,
                'X-COILS-WORKFLOW-OUTPUT-URL': paths['output'],
            }
        )

    def do_DELETE(self):
        """
        Implement DELETE operation.

        Terminates a process, or deletes a completed process
        """
        try:
            self.context.run_command('route::delete', object=self.entity)
            self.context.commit()
        except:
            self.request.simple_response(500, message='Deletion failed')
        else:
            self.request.simple_response(204, message='No Content')
