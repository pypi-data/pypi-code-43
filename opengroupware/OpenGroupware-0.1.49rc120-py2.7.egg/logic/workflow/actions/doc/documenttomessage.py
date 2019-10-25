#
# Copyright (c) 2014, 2015
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
import shutil
from coils.core import \
    walk_ogo_uri_to_target, \
    Document, \
    CoilsException, \
    BLOBManager
from coils.core.logic import ActionCommand


class DocumentToMessageAction(ActionCommand):
    """
    Copy the contents of a document to a message, retaining the MIME type.
    """
    __domain__ = "action"
    __operation__ = "document-to-message"
    __aliases__ = ['documentToMessage', 'documentToMessageAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._mimetype

    def do_action(self):

        if not self._document_id:
            # Document not specified by ID, assume we are using a URI
            document = walk_ogo_uri_to_target(
                context=self._ctx,
                uri=self._document_uri,
            )
            if not isinstance(document, Document):
                raise CoilsException(
                    'Unable to marshall document by uri "{0}"'
                    .format(self._document_uri, )
                )
        else:
            # Document specified by ID
            document = self._ctx.run_command(
                'document::get', id=self._document_id,
            )
            if not isinstance(document, Document):
                raise CoilsException(
                    'Unable to marshall document by id "{0}"'
                    .format(self._document_id, )
                )

        # Open the document
        handle = self._ctx.run_command(
            'document::get-handle', document=document,
        )
        if handle is None:
            raise CoilsException(
                'Unable to open document content for OGo#{0}'.
                format(document.object_id, )
            )

        # Copy document contents to command output
        shutil.copyfileobj(handle, self.wfile)

        # Preserve MIME type of document for action MIME type
        self._mimetype = self._ctx.type_manager.get_mimetype(entity=document)

        # Close Document
        BLOBManager.Close(handle)

        # Dereference document entity
        document = None

    def parse_action_parameters(self):

        self._document_uri = None

        self._document_id = None

        # default is to use the more specific documentId if specified
        self._document_id = self.process_label_substitutions(
            self.action_parameters.get('documentId', None, )
        )
        if not self._document_id:
            # As document_id was not specified lets try to find a URI
            self._document_uri = self.process_label_substitutions(
                self.action_parameters.get('documentURI', None, )
            )
