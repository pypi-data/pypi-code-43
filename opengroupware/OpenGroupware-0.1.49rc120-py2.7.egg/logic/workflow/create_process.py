#
# Copyright (c) 2009, 2011, 2012, 2013, 2015, 2016
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
import os
import pickle
import shutil
import traceback
from sqlalchemy import and_
from xml.sax import make_parser
from bpml_handler import BPMLSAXHandler
from coils.core import BLOBManager, CoilsException, Process
from coils.core.logic import CreateCommand
from keymap import COILS_PROCESS_KEYMAP
from utility import \
    filename_for_process_markup, \
    filename_for_process_code, \
    filename_for_route_markup, \
    parse_property_encoded_acl_list, \
    WF_RUNCONTROL_QUASH_MULTIQUEUE

INHERITED_PROPERTIES = (
    ('http://www.opengroupware.us/oie', 'disableStateVersioning', ),
    ('http://www.opengroupware.us/oie', 'singleton', ),
    ('http://www.opengroupware.us/oie', 'preserveAfterCompletion', ),
    ('http://www.opengroupware.us/oie', 'archiveAfterExpiration', ),
    ('http://www.opengroupware.us/oie', 'expireDays', ),
    ('http://www.opengroupware.us/oie', 'routeGroup', ),
)


class CreateProcess(CreateCommand):
    __domain__ = "process"
    __operation__ = "new"

    def __init__(self):
        CreateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap = COILS_PROCESS_KEYMAP
        self.entity = Process
        CreateCommand.prepare(self, ctx, **params)

    def audit_action(self):
        CreateCommand.audit_action(self)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self.do_rewind = params.get('rewind', True)
        self._origin_label = params.get('origin_label', 'input')
        self._xattrs = params.get('xattrs', dict())
        if ('data' in params):
            self.values['data'] = params['data']
        elif ('filename' in params):
            self.values['handle'] = os.open(params['filename'], 'rb')
        elif ('handle' in params):
            self.values['handle'] = params['handle']
        self._mimetype = params.get('mimetype', 'application/octet-stream')

    def copy_markup(self, route):
        # TODO: Error meaningfully if the route has no markup
        source = BLOBManager.Open(filename_for_route_markup(route), 'rb')
        if not source:
            raise CoilsException(
                'Unable to read source (route markup) from "{0}"'.
                format(filename_for_route_markup(route), )
            )
        target = BLOBManager.Create(
            filename_for_process_markup(self.obj),
            encoding='binary',
        )
        shutil.copyfileobj(source, target)
        target.flush()
        source.seek(0)
        bpml = source.read()
        BLOBManager.Close(source)
        BLOBManager.Close(target)
        self.obj.set_markup(bpml)

    def compile_markup(self):
        # TODO: Use the markup already in memory!
        handle = BLOBManager.Open(
            filename_for_process_markup(self.obj), 'rb',
            encoding='binary',
        )
        parser = make_parser()
        handler = BPMLSAXHandler()
        parser.setContentHandler(handler)
        parser.parse(handle)
        code = handler.get_processes()
        BLOBManager.Close(handle)
        handle = BLOBManager.Create(
            filename_for_process_code(self.obj),
            encoding='binary',
        )
        pickle.dump(code, handle)
        BLOBManager.Close(handle)

    def copy_default_acls_from_route(self, process, route):
        default_acls = self._ctx.property_manager.get_property(
            entity=route,
            namespace='http://www.opengroupware.us/oie',
            name='defaultProcessACLs',
        )
        if default_acls:
            try:
                acls = parse_property_encoded_acl_list(
                    default_acls.get_value()
                )
                if acls:
                    for acl in acls:
                        self._ctx.run_command(
                            'object::set-acl',
                            object=process,
                            context_id=int(acl[0]),
                            action=acl[1],
                            permissions=acl[2],
                        )
                        self.log.debug(
                            'Applied default ACL for contextId#{0} to '
                            'OGo#{1} [Process]'.format(
                                int(acl[0]),
                                process.object_id,
                            )
                        )
            except CoilsException, e:
                message = traceback.format_exc()
                self.log.exception(e)
                if (self._ctx.amq_available):
                    self._ctx.send_administrative_notice(
                        category='workflow',
                        urgency=7,
                        subject=(
                            'Unable to apply defaultProcessACLs value to '
                            'processId#{0}'.format(
                                process.object_id,
                            )
                        ),
                        message=message)
                return False
            else:
                return True
        else:
            return True

    def inherit_properties_from_route(self, process, route):
        for propset in INHERITED_PROPERTIES:
            prop = self._ctx.property_manager.get_property(
                entity=route,
                namespace=propset[0],
                name=propset[1],
            )
            if prop:
                self.log.debug(
                    'Inheritting object property {{{0}}}{1} from OGo#{2} '
                    '[route] to OGo#{3} [process]'.format(
                        propset[0],
                        propset[1],
                        route.object_id,
                        process.object_id,
                    )
                )

    def run(self, **params):
        '''
        TODO: Verify MIME f input message against MIME of input message for
        route.
        '''
        CreateCommand.run(self, **params)

        # Verify route id
        route = None
        if self.obj.route_id:
            route = self._ctx.run_command(
                'route::get',
                id=self.obj.route_id,
                access_check=self.access_check,
            )
        if not route:
            # TODO Support ad-hoc processes
            raise CoilsException('No such route or route not available')

        # Route is available

        """ RUN CONTROL FLAGS """
        if route.runcontrol:
            if (route.runcontrol & WF_RUNCONTROL_QUASH_MULTIQUEUE):
                """
                supress process creation if an instance of the route (a
                process) is already in the queued state.
                """
                queued_count = self._ctx.db_session().query(Process).filter(
                    and_(
                        Process.route_id == route.object_id,
                        Process.state == 'Q',
                    )
                ).count()
                if queued_count:
                    if (self._ctx.amq_available):
                        self._ctx.send_administrative_notice(
                            category='workflow',
                            urgency=5,
                            subject=(
                                'Process creation prevented by run-control'
                            ),
                            message=(
                                'Creation of process from OGo#{0} [Route] '
                                '"{1}" by {2} prohibited by QUASH_MULTIQUEUE'
                                ' run-control directive.\n'
                                '{3} queued processes present.'.format(
                                    route.object_id,
                                    route.name,
                                    self._ctx.get_login(),
                                    queued_count,
                                )
                            ),
                        )
                    self.set_return_value(None)
            # End WF_RUNCONTROL_QUASH_MULTIQUEUE

        """ END RUN CONTROL FLAGS """

        # Allocate the input message of the process
        message = None
        if ('data' in self.values):
            message = self._ctx.run_command(
                'message::new',
                process=self.obj,
                mimetype=self._mimetype,
                label=u'InputMessage',
                data=self.values['data'],
            )
        elif ('handle' in self.values):
            message = self._ctx.run_command(
                'message::new',
                process=self.obj,
                mimetype=self._mimetype,
                label=u'InputMessage',
                rewind=self.do_rewind,
                handle=self.values['handle'],
            )
        else:
            raise CoilsException('Cannot create process without input')
        self.obj.input_message = message.uuid

        if not self.obj.priority:
            prop = self._ctx.property_manager.get_property(
                entity=route,
                namespace='http://www.opengroupware.us/oie',
                attribute='defaultPriority',
            )
            if prop:
                try:
                    self.obj.priority = int(prop.get_value())
                except Exception:
                    pass
        if not self.obj.priority:
            self.obj.priority = 125
        elif self.obj.priority < 0:
            self.obj.priority = 125
        elif self.obj.priority > 255:
            self.obj.priority = 125

        self.copy_markup(route)
        self.compile_markup()
        self.save()
        shelf = BLOBManager.OpenShelf(uuid=self.obj.uuid)
        shelf.close()

        self.copy_default_acls_from_route(self.obj, route)

        self.inherit_properties_from_route(self.obj, route)

        """
        Set origin label
        """
        self._ctx.property_manager.set_property(
            entity=self.obj,
            namespace='http://www.opengroupware.us/oie',
            attribute='originLabel',
            value=self._origin_label,
        )

        """
        Apply XATTR Values provided in parameters to process
        """
        for key, value in self._xattrs.items():
            if value is None:
                value = 'YES'
            elif isinstance(value, list):
                value = str(value[0])
            self._ctx.property_manager.set_property(
                entity=self.obj,
                namespace='http://www.opengroupware.us/oie',
                attribute='xattr_{0}'.format(key.lower().replace(' ', '')),
                value=value,
            )

        """
        Audit the creation of the process on the route's audit log.
        Note that this must be the LAST section of process::new.  Add
        anything else PRIOR to this section.
        """

        self._ctx.flush()
        self._ctx.db_session().refresh(self.obj)

        prop = self._ctx.property_manager.get_property(
            entity=route,
            namespace='http://www.opengroupware.us/oie',
            attribute='recordProcessCreation',
        )
        if not prop:
            return
        if not (prop.get_string_value() == 'YES'):
            return
        if not route:
            """No route!  nothing to record audit into"""
            return
        owner = self._ctx.run_command('account::get', id=self.obj.owner_id, )
        if not owner:
            """No owner?!?!"""
            return
        # compose first line of audit message
        messages = [
            (
                'process OGo#{0} queued by OGo#{1} '
                'as "{2}" OGo#{3} with priority {4}.'
                .format(
                    self.obj.object_id,
                    self._ctx.identity_id,
                    owner.login,
                    owner.object_id,
                    self.obj.priority,
                )
            )
        ]
        owner = None
        # record object properties of process to audit message, one per line
        for prop in self._ctx.property_manager.get_properties(self.obj):
            if prop.get_hint() == 'data':
                """
                Data values just become "..." as the audit long does not
                support arbitrary binary data
                """
                string_value = '...'
            else:
                string_value = prop.get_string_value()
            messages.append(
                '    {{{0}}}{1} = [{2}] "{3}"'
                .format(
                    prop.namespace,
                    prop.name,
                    prop.get_hint(),
                    string_value,
                )
            )

        self.log.info(
            'Recording process created on route\'s audit log.\n{0}'
            .format('\n'.join(messages, ), )
        )

        self._ctx.audit_at_commit(
            object_id=self.obj.route_id,
            action='10_commented',
            message='\n'.join(messages, ),
        )
