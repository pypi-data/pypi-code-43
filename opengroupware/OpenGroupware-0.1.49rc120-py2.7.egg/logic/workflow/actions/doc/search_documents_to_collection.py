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
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from command import DocumentBaseAction
from coils.foundation import qsearch_from_xml


class SearchDocumentsToCollectionAction(ActionCommand, DocumentBaseAction):
    """
    Assign documents matching specified criteria to a Collection
    """
    __domain__ = "action"
    __operation__ = "search-documents-to-collection"
    __aliases__ = [
        'searchDocumentsToCollection',
        'searchDocumentsToCollectionAction',
    ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'text/plain'

    def do_action(self):

        collection = self._marshall_collection(
            collection_name=self._collection_name,
            collection_kind=self._collection_kind,
            collection_acls=self._collection_acls,
            project_uri=self._project_uri,
            create=self._create_collection,
        )

        entity, criteria, limit, detail_level, sort_by = \
            qsearch_from_xml(self._qsearch_text)

        documents = self._ctx.run_command(
            'document::search',
            criteria=criteria,
            limit=limit,
            orm_hints=(detail_level, ),
            sort_keys=sort_by,
        )

        self.log_message(
            'Retrieved {0} documents via document search'
            .format(len(documents), ),
            category='debug',
        )

        for document in documents:
            self.context.r_c(
                'object::assign-to-collection',
                collection=collection,
                entity=document,
            )

        self.log_message(
            'Assigned {0} documents to collection OGo#{1}'
            .format(len(documents), collection.object_id, ),
            category='debug',
        )

        self.wfile.write(str(collection.object_id))

    def parse_action_parameters(self):

        qsearch_text = self.process_label_substitutions(
            self.action_parameters.get('qsearch', '')
        )
        if not qsearch_text:
            raise CoilsException(
                'No qsearch criteria specified in '
                'searchDocumentsToCollectionAction'
            )

        '''collectionName'''
        self._collection_name = \
            self.process_label_substitutions(
                self.action_parameters.get('collectionName', None)
            )

        '''collectionKind'''
        self._collection_kind = \
            self.process_label_substitutions(
                self.action_parameters.get('collectionKind', '')
            )
        if self._collection_kind == '':
            self._collection_kind = None

        '''collectionACLs'''
        self._collection_acls = \
            self.process_label_substitutions(
                self.action_parameters.get('collectionACLs', '')
            )
        if self._collection_acls == '':
            self._collection_acls = None

        '''collectionProject'''
        self._project_uri = \
            self.process_label_substitutions(
                self.action_parameters.get('collectionProject', '')
            )
        if self._project_uri == '':
            self._project_uri = None

        '''createCollection'''
        create_collection = \
            self.process_label_substitutions(
                self.action_parameters.get('createCollection', 'NO')
            )
        self._create_collection = False
        if create_collection.strip().upper() == 'YES':
            self._create_collection = True

    def do_epilogue(self):
        pass
