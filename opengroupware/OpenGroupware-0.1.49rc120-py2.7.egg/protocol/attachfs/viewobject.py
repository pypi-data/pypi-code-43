#
# Copyright (c) 2011, 2012, 2014, 2015, 2016
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
from pprint import pformat
from coils.core import NoSuchPathException
from coils.net import PathObject
from documentobject import DocumentObject
from attachmentobject import AttachmentObject
from messageobject import MessageObject
from processobject import ProcessObject
from contactobject import ContactObject
from enterpriseobject import EnterpriseObject
from dateobject import DateObject
from projectobject import ProjectObject
from routeobject import RouteObject


class ViewObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        if self.name == 'download':
            disposition = 'attachment'
        else:
            disposition = 'inline'

        criteria = None
        kind = None
        if name.isdigit():
            kind = self.context.type_manager.get_type(int(name))
            if kind == 'Document':
                """We search for documents, all other types are retrieved
                using the objectId; we search for documents to enable the
                flexibility that document retrieval requires."""
                criteria = [
                    {
                        'key': 'objectId',
                        'value': int(name),
                        'expression': 'EQUALS',
                    }
                ]
        elif name.startswith('sha512.'):
            kind = 'Document'
            criteria = [
                {
                    'key': 'checksum',
                    'value': name[len('sha512.'):],
                    'expression': 'EQUALS',
                }
            ]
        else:
            kind = 'attachment'

        if kind == 'attachment':
            # First try the name as an attachment UUID
            entity = self.context.run_command('attachment::get', uuid=name, )
            if entity:
                return AttachmentObject(
                    self,
                    name,
                    entity=entity,
                    disposition=disposition,
                    parameters=self.parameters,
                    request=self.request,
                    context=self.context, )

            '''
            If the name was not found as an attachment UUID,
            try it as a message UUID
            '''
            if name.startswith('{'):
                message_uuid = name
            else:
                message_uuid = '{{{0}}}'.format(name, )
            entity = self.context.run_command('message::get',
                                              uuid=message_uuid, )
            if entity:
                return MessageObject(
                    self, name, entity=entity,
                    disposition=disposition,
                    parameters=self.parameters,
                    request=self.request,
                    context=self.context, )

            # We didn't find it as an attachment or message UUID
            # TODO: Implement alias support
            raise NoSuchPathException(
                'Unable to access object "{0}"'.format(name, )
            )

        elif kind == 'Document':
            """Perform search for document"""
            results = self.context.run_command(
                'document::search',
                criteria=criteria,
                orm_hints=(0, ),
                )
            if not results:
                raise NoSuchPathException(
                    'No documents match criteria "{0}"'
                    .format(pformat(criteria), )
                )
            if len(results) > 1:
                raise NoSuchPathException(
                    'Multiple documents match criteria "{0}"; '
                    'this violates AttachFS expectations.'
                    .format(pformat(criteria), )
                )
            entity = results[0]
            return DocumentObject(
                self, name, entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        elif kind == 'Process':
            entity = self.context.run_command('process::get',
                                              id=int(name), )
            if not entity:
                raise NoSuchPathException(
                    'Unable to access objectId#{0}'.format(name, ))
            return ProcessObject(
                self, name, entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        elif kind == 'Route':
            entity = self.context.run_command('route::get',
                                              id=int(name), )
            if not entity:
                raise NoSuchPathException(
                    'Unable to access objectId#{0}'.format(name, ))
            return RouteObject(
                self, name, entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        elif kind == 'Project':
            entity = self.context.run_command('project::get',
                                              id=int(name), )
            if not entity:
                raise NoSuchPathException(
                    'Unable to access objectId#{0}'.format(name, ))
            return ProjectObject(
                self, name, entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        elif kind == 'Contact':
            entity = self.context.run_command(
                'contact::get', id=int(name),
            )
            if not entity:
                raise NoSuchPathException(
                    'Unable to access objectId#{0}'.format(name, )
                )
            return ContactObject(
                self, name,
                entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        elif kind == 'Enterprise':
            entity = self.context.run_command(
                'enterprise::get', id=int(name),
            )
            if not entity:
                raise NoSuchPathException(
                    'Unable to access objectId#{0}'.format(name, )
                )
            return EnterpriseObject(
                self, name,
                entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        elif kind == 'Appointment':
            entity = self.context.run_command(
                'appointment::get', id=int(name),
            )
            if not entity:
                raise NoSuchPathException(
                    'Unable to access objectId#{0}'.format(name, )
                )
            return DateObject(
                self, name,
                entity=entity,
                disposition=disposition,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        else:
            raise NoSuchPathException(
                'Unable to access object via attachfs.'
            )

    def supports_DELETE(self):
        return True

    def do_DELETE(self, name):

        attachment = self.context.run_command('attachment::get', uuid=name, )
        if not attachment:
            raise NoSuchPathException(
                'Attachment "{0}" does not exist'.format(name, )
            )

        result = self.context.run_command(
            'attachment::delete',
            uuid=attachment.uuid,
        )

        self.context.commit()

        self.request.simple_response(204)
