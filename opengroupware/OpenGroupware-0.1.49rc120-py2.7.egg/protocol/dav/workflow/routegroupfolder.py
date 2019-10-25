# Copyright (c) 2018, 2019
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
from coils.core import \
    AccessForbiddenException, \
    NotImplementedException, \
    CoilsException, \
    BLOBManager
from coils.net import DAVFolder, OmphalosCollection
from routefolder import RouteFolder
from signalobject import SignalObject
from workflow import WorkflowPresentation
from utility import compile_bpml


class RouteGroupFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return False

    def supports_MKCOL(self):
        return True

    def _load_contents(self):
        self.data = {}
        if not hasattr(self, 'entity'):
            # 'root' route group folder
            self.log.debug('Returning enumeration of available routes.')
            groups = self.context.run_command('routegroup::get', )
            for group in groups:
                self.insert_child(group.name, group)
        else:
            # route group folder for a specified route
            routes = self.context.run_command(
                'route::search',
                criteria=[
                    {'key': 'group_id', 'value': self.entity.object_id, }
                ],
                orm_hints=(0, ),
            )
            for route in routes:
                self.insert_child(route.name, route)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        #
        # Support retriving a specific key without loading all the routes
        #
        if (name == 'signal'):
            return SignalObject(
                self, name,
                parameters=self.parameters,
                entity=None,
                context=self.context,
                request=self.request,
            )
        elif (name in ('.ls', '.json', '.contents')):
            # REST Request
            if (self.load_contents()):
                if (name in ('.json', '.contents')):
                    return OmphalosCollection(
                        self, name,
                        detailLevel=65535,
                        rendered=True,
                        data=self.get_children(),
                        parameters=self.parameters,
                        context=self.context,
                        request=self.request,
                    )
                elif (name == '.ls'):
                    return OmphalosCollection(
                        self, name,
                        rendered=False,
                        data=self.get_children(),
                        parameters=self.parameters,
                        context=self.context,
                        request=self.request,
                    )
        elif hasattr(self, 'entity'):
            # children are routes, so spawn a Routefolder
            if self.is_loaded:
                route = self.get_child(name)
            else:
                route = self.context.run_command('route::get', name=name)
            if route:
                return RouteFolder(
                    self, name,
                    parameters=self.parameters,
                    entity=route,
                    context=self.context,
                    request=self.request,
                )
        else:
            # children are route groups, so spawn an RouteGroupFolder
            if self.is_loaded:
                routegroup = self.get_child(name)
            else:
                routegroup = self.context.run_command(
                    'routegroup::get', name=name,
                )
            if routegroup:
                return RouteGroupFolder(
                    self, name,
                    parameters=self.parameters,
                    entity=routegroup,
                    context=self.context,
                    request=self.request,
                )
        raise self.no_such_path()

    #
    # MKCOL
    #

    def do_MKCOL(self, name):
        '''
           TODO: Implement a good failure response

           201 (Created) - The collection or structured resource was created in
           its entirety.

           403 (Forbidden) - This indicates at least one of two conditions: 1)
           the server does not allow the creation of collections at the given
           location in its namespace, or 2) the parent collection of the
           Request-URI exists but cannot accept members.

           405 (Method Not Allowed) - MKCOL can only be executed on a
           deleted/non-existent resource.

           409 (Conflict) - A collection cannot be made at the Request-URI
           until one or more intermediate collections have been created.

           415 (Unsupported Media Type)- The server does not support the
           request type of the body.

           507 (Insufficient Storage) - The resource does not have sufficient
           space to record the state of the resource after the execution of
           this method.
        '''

        name_in_use = self.context.run_command(
            'routegroup::get', name=name,
        )
        if name_in_use:
            raise AccessForbiddenException('Name already in use')

        child = self.context.run_command(
            'routegroup::new', values={'name': name, }
        )

        if child:
            self.context.commit()
            # group created
            self.request.simple_response(201)
        else:
            # group not created . . . why?
            self.request.simple_response(403)

    def do_PUT(self, request_name):
        """
        Create route from markup PUT to the RouteGroup folder
        """
        if not hasattr(self, 'entity'):
            """this folde is the root groups folder"""
            raise NotImplementedException()

        bpml = BLOBManager.ScratchFile(suffix='bpml')
        bpml.write(self.request.get_request_payload())
        description, cpm = compile_bpml(bpml, log=self.log)
        BLOBManager.Close(bpml)
        try:
            route = self.context.run_command(
                'route::new',
                values=description,
                markup=self.request.get_request_payload(),
            )
            route.group_id = self.entity.object_id
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Route creation failed.')
        self.context.commit()
        self.request.simple_response(
            301,
            headers={
                'Location': '/dav/Workflow/Groups/{0}/{1}/markup.xml'
                .format(self.name, route.name, ),
                'Content-Type': 'text/xml',
            }
        )
