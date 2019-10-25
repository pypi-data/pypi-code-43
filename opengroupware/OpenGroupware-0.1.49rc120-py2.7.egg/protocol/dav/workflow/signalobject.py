# Copyright (c) 2009, 2014, 2015, 2016
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from StringIO import StringIO
from coils.core import CoilsException, NotImplementedException
from coils.net import DAVObject
from workflow import WorkflowPresentation


class SignalObject(DAVObject, WorkflowPresentation):
    """Represent a Signal to a workflow object,  signals are GET requests"""

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def _signal_route(self, key, value, ):
        route_id = self.entity.object_id

        if key == 'inputmessage':
            self.log.debug(
                'Attempting to create new process from route {0}'
                .format(route_id, )
            )
            try:
                process = self.create_process(
                    route=self.entity, data=value,
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
                    return

                # Retrieve XATTR values from URL parameters
                for key, value in self.parameters.items():
                    if (key.startswith('xattr.')):
                        prop_name = 'xattr_{0}'.format(key[6:].lower())
                        if (len(value) > 0):
                            prop_value = str(value[0])
                        else:
                            prop_value = 'YES'
                        self.context.property_manager.set_property(
                            process,
                            'http://www.opengroupware.us/oie',
                            prop_name,
                            prop_value,
                        )
                    elif key == 'label':
                        """
                        Set the origin label property to the name of the
                        label parameter
                        """
                        label = str(value[0])
                        self.context.property_manager.set_property(
                            entity=process,
                            namespace='http://www.opengroupware.us/oie',
                            attribute='originLabel',
                            value=label.replace('\\', '_').replace('/', '_'),
                        )

                # COMMIT
                self.context.commit()
                self.log.info(
                    'Process {0} created via signal by {1}.'.
                    format(
                        process.object_id,
                        self.context.get_login(),
                    )
                )
                message = self.get_input_message(process)
                self.start_process(process)
            except Exception, e:
                self.log.exception(e)
                raise CoilsException('Failed to create process')
            w = StringIO()
            paths = self.get_process_urls(process)
            w.write(
                'OK PID:{0} MSG{1} WATCH:{2}'
                .format(
                    process.object_id,
                    message.uuid,
                    paths['output'],
                )
            )
            self.request.simple_response(
                200,
                data=w.getvalue(),
                mimetype='text/plain',
                headers={
                    'X-COILS-WORKFLOW-MESSAGE-UUID':  message.uuid,
                    'X-COILS-WORKFLOW-MESSAGE-LABEL': message.label,
                    'X-COILS-WORKFLOW-PROCESS-ID': process.object_id,
                    'X-COILS-WORKFLOW-OUTPUT-URL': paths['output'],
                },
            )
            return

        raise CoilsException(
            'Workflow presentation object does not understand '
            'signal key {0}'.format(key, )
        )

    def _signal_process(self, key, value, ):
        if key == 'kill':
            raise NotImplementedException(
                'Process kill signal is not yet implemented'
            )
        elif key == 'park':
            raise NotImplementedException(
                'Process park signal is not yet implemented'
            )
        elif key == 'start':
            raise NotImplementedException(
                'Process start signal is not yet implemented'
            )
        elif key == 'message':
            # label = self.parameters.get('label')[0]
            raise NotImplementedException(
                'Process message signal is not yet implemented'
            )

        self.request.simple_response(200)

    def do_GET(self):

        if not (
            ('key' in self.parameters) and ('value' in self.parameters)
        ):
            raise CoilsException(
                'Workflow signals must contain a key and value parameter.'
            )

        key = self.parameters.get('key')[0].lower()
        value = self.parameters.get('value')[0]

        if (self.entity is None):
            self.signal_queue_manager()
            self.request.simple_response(201)
            return
        elif (self.entity.__entityName__ == 'Route'):
            self._signal_route(key, value, )
        elif (self.entity.__entityName__ == 'Process'):
            self._signal_process(key, value, )
        else:
            raise NotImplementedException(
                'This workflow presentation object does not support signals.'
            )
