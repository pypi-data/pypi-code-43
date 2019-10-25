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


class SearchDocumentsForUncollectionAction(ActionCommand, DocumentBaseAction):
    """
    Relieve collection membership of documents matching specified criteria
    """
    __domain__ = "action"
    __operation__ = "search-documents-for-uncollection"
    __aliases__ = [
        'searchDocumentsForUncollection',
        'searchDocumentsForUncollectionAction',
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
            create=False,
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

        counter = 0
        for document in documents:
            if self._ctx.r_c(
                'collection::delete-assignment',
                collection=collection,
                entity=document,
            ):
                self.log_message(
                    'Unassigned OGo#{0} [Document] from collection OGo#{1}'
                    .format(document.object_id, collection.object_id, ),
                    category='debug',
                )
                counter += 1

        self.log_message(
            'Unassigned {0} documents from collection OGo#{1}'
            .format(counter, collection.object_id, ),
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
                'searchDocumentsForUncollectionAction'
            )
        self._qsearch_text = qsearch_text

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

    def do_epilogue(self):
        pass
