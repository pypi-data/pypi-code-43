#
# Copyright (c) 2015
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
import base64
from datetime import datetime
from coils.core import \
    NotImplementedException, \
    ogo_uri_to_project, \
    CoilsException, \
    parse_encoded_acl_list
from coils.foundation.api.elementflow import elementflow


def serialize_property_value(hint, value):

    if hint == 'data':
        value = base64.base64_encode(value)
    elif hint == 'oid':
        raise NotImplementedException(
            'OID type in document metadata manifest is not implemented'
        )

    if isinstance(value, basestring):
        return value
    elif isinstance(value, int) or isinstance(value, long):
        return unicode(value)
    elif isinstance(value, float):
        return unicode(value)
    elif isinstance(value, datetime):
        return unicode(value.strftime('%Y-%m-%d %H:%M:%S'))


class DocumentBaseAction(object):

    def _create_collection(
        self,
        collection_name,
        collection_kind,
        collection_acls,
        project_uri,
    ):
        collection = self._ctx.r_c(
            'collection::new', values={
                'name': collection_name,
                'kind': collection_kind,
            },
        )
        self.log_message(
            'Automatically created new collection OGo#{0} named "{1}"'
            .format(collection.object_id, collection.title, ),
            category='info',
        )

        """ACLS"""
        acls = parse_encoded_acl_list(collection_acls)
        if acls:
            for acl in acls:
                self._ctx.run_command(
                    'object::set-acl',
                    object=collection,
                    context_id=int(acl[0]),
                    action=acl[1],
                    permissions=acl[2],
                )
                self.log_message(
                    'Applied default ACL for contextId#{0} to '
                    'OGo#{1} [Document]'.format(
                        int(acl[0]),
                        collection.object_id,
                    ),
                    category='debug',
                )

        """Assign collection to project if specified"""
        if self._project_uri:
            project = ogo_uri_to_project(
                self._ctx, self._project_uri,
            )
            if not project:
                raise CoilsException(
                    'Unable to marshall project from URI "{0}" for assignment '
                    'of new collection to project.'
                    .format(self._project_uri, )
                )
            collection.project_id = project.object_id
            self.log_message(
                'New collection OGo#{0} assigned to project "{1}" OGo#{2}'
                .format(
                    collection.object_id,
                    project.number,
                    project.object_id,
                ),
                category='debug',
            )
        return collection

    def _marshall_collection(
        self,
        collection_name,
        collection_kind=None,
        collection_acls=None,
        project_uri=None,
        create=True,
    ):
        """
        Manifest the collection to which documents must be assigned
        """

        criteria = [{'key': 'name', 'value': collection_name, }, ]
        if collection_kind:
            criteria.append(
                {'key': 'kind', 'value': collection_kind, },
            )

        collection = self._ctx.run_command(
            'collection::search', criteria=criteria,
        )
        if not collection and create:
            collection = self._create_collection(
                collection_name,
                collection_kind,
                collection_acls,
                project_uri,
            )
        elif not collection and not create:
            raise CoilsException(
                'No Collection corresponds to the specified criteria:'
                'name="{0}" kind={1}'
                .format(collection_name, collection_kind, )
            )
        else:
            '''
            Searches always have multiple results, we are taking the first one
            '''
            collection = collection[0]
            self.log_message(
                'Discovered OGo#{0} [Collection] that matches descriptor'
                .format(collection.object_id, ),
                category='debug',
            )

        return collection

    def get_file_name(self, document):
        return document.get_file_name()

    def generate_manifest(self, documents, wfile):

        with elementflow.xml(wfile, u'metadata', indent=True) as response:
            for document in documents:

                with response.container(
                    'object',
                    attrs={
                        'name': self.get_file_name(document),
                        'size': str(document.file_size),
                        'version': str(document.version),
                        'objectId': str(document.object_id),
                    }
                ):
                    if document.checksum:
                        response.element(
                            'checksum',
                            attrs={'checksumMode': 'SHA512', },
                            text=document.checksum,
                        )
                    for prop in self._ctx.pm.get_properties(document):
                        response.element(
                            'objectProperty',
                            attrs={
                                'name': '{{{0}}}{1}'.format(
                                    prop.namespace, prop.name,
                                ),
                                'typeHint': prop.get_hint(),
                            },
                            text=serialize_property_value(
                                prop.get_hint(), prop.get_value(),
                            ),
                        )
