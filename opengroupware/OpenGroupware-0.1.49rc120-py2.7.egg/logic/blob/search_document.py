#
# Copyright (c) 2011, 2013, 2014, 2015, 2016
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
from coils.foundation import Document
from coils.core.logic import SearchCommand
from coils.core import CoilsException, walk_ogo_uri_to_folder
from keymap import COILS_DOCUMENT_KEYMAP
from coils.foundation import apply_orm_hints_to_query


def descend_yielding(context, folder, depth=0, maxdepth=-1, ):
    yield folder
    if (
        maxdepth < 0 or
        depth < maxdepth
    ):
        for candidate in folder.folders:
            for child in descend_yielding(context=context,
                                          folder=candidate,
                                          depth=depth + 1,
                                          maxdepth=maxdepth, ):
                yield child


class SearchDocuments(SearchCommand):
    __domain__ = "document"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCommand.__init__(self)

    def prepare(self, ctx, **params):
        SearchCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def _custom_search_criteria(self, key, value, conjunction, expression, ):

        if len(key) > 1:
            # No compound custom keys supported
            return (None, None, None, None, None, )

        key = key[0]

        if key in ('folderuri', 'nullablefolderuri'):
            allow_no_destination = False
            if key == 'nullablefolderuri':
                allow_no_destination = True
            """
            search criteria uses a key of folderuri which can either be
            EQUALS an OGo URI, or IN a list of OGo URIs.  All the URIs
            must resolve to a destination or an exception will be
            raised.
            """
            folder_uris = None
            folder_ids = list()
            if expression == 'EQUALS':
                folder_uris = [value, ]  # single value to list
            elif expression == 'IN':
                if isinstance(value, basestring):
                    # string value for IN is assumed to be a CSV value
                    value = [x.strip() for x in value.split(',')]
                folder_uris = value  # assuming value is a list
            else:
                raise CoilsException(
                    'Only EQUALS and IN supported as expression for '
                    '"folderuri", expression is "{0}"'.format(expression, )
                )
            for folder_uri in folder_uris:
                try:
                    folder, params = walk_ogo_uri_to_folder(
                        self._ctx, folder_uri, create_path=False,
                    )
                except CoilsException as exc:
                    if not allow_no_destination:
                        raise exc
                else:
                    if folder:
                        folder_ids.append(folder.object_id, )
            return (Document, 'folder_id', folder_ids, conjunction, 'IN', )

        if key == 'topfolderid' and expression == 'EQUALS':

            folder_id = None
            try:
                folder_id = long(value)
            except:
                raise CoilsException(
                    'Non-numeric value passed to search criteria topFolderId'
                )

            folder = self._ctx.r_c('folder::get', id=folder_id, )
            if not folder:
                raise CoilsException(
                    'Value "{0}" provided for topFolderId criteria of document'
                    ' search does not materialize to a Folder entity'.
                    format(value, )
                )

            folder_ids = list()
            folder_ids.extend([
                x.object_id for x in
                descend_yielding(self._ctx, folder, maxdepth=25, )
            ])

            return (Document, 'folder_id', folder_ids, conjunction, 'IN', )

        if key == 'collectionname' and expression == 'EQUALS':
            collection = self._ctx.r_c('collection::get', name=value, )
            if not collection:
                raise CoilsException(
                    'Unable to marshall Collection named "{0}" in order to '
                    'construct search criteria.'
                    .format(value, )
                )
            key = 'collectionid'
            value = collection.object_id

        if key == 'collectionid' and expression == 'EQUALS':

            try:
                collection_id = long(value)
            except:
                raise CoilsException(
                    'Non-numeric value passed to search criteria collectionId'
                )
            collection = self._ctx.r_c(
                'collection::get', id=collection_id,
            )
            if not collection:
                raise CoilsException(
                    'Value "{0}" provided for collectionId criteria of '
                    'document search does not materialize to a Collection '
                    'entity'.format(collection_id, )
                )
            assigned_ids = [
                x.assigned_id for x in collection.assignments
            ]

            return (Document, 'object_id', assigned_ids, conjunction, 'IN', )

        # unsupported custom key
        return (None, None, None, None, None, )

    def add_result(self, document):
        if (document not in self._result):
            self._result.append(document)

    def run(self):
        keymap = COILS_DOCUMENT_KEYMAP.copy()
        keymap.update(
            {
                'created':         ['created', 'date', None, ],
                'creator_id':      ['creator_id', 'int', None, ],
                'creatorid':       ['creator_id', 'int', None, ],
                'creatorobjectid': ['creator_id', 'int', None, ],
                'ownerid':         ['owner_id', 'int', None, ],
                'owner_id':        ['owner_id', 'int', None, ],
                'ownerobjectid':   ['owner_id', 'int', None, ],
                'modified':        ['modified', 'date', None, ],
            }
        )
        self._query = apply_orm_hints_to_query(
            self._parse_criteria(self._criteria, Document, keymap),
            Document,
            self.orm_hints,
        )
        data = self._query.all()
        self.log.debug('query returned {0} objects'.format(len(data), ))
        self.set_return_value(data)
        return
