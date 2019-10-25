#
# Copyright (c) 2015, 2016
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
import zipfile
from scrubbrush import ScrubBrush
from coils.core import BLOBManager, CoilsException, ObjectProperty
from coils.core.logic import ActionCommand
from command import DocumentBaseAction

"""
WARN: this action appears to be very incomplete!
"""


class CollectionToZIPFileAction(ActionCommand, DocumentBaseAction):
    """
    Archive the documents assigned to a collection into a ZIP file
    """
    __domain__ = "action"
    __operation__ = "collection-to-zipfile"
    __aliases__ = ['collectionToZipFile', 'collectionToZipFileAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def do_action(self):

        collection = self._marshall_collection(
            collection_name=self._collection_name,
            collection_kind=self._collection_kind,
            collection_alcs=self._collection_aclk,
            project_uri=self._project_uri,
            create=False,
        )

        self.log_message(
            'Retrieving documents from OGo#{0} [Collection] named "{1}"'
            .format(collection.object_id, collection.title, ),
            category='debug',
        )

        """Prepare MIME-type filter"""
        if 'any' in self.mimetypes_to_include:
            self.log_message(
                'MIMETypes includes "any", all documents will be included',
                category='info',
            )
        else:
            self.log_message(
                'The following document types will be included: {0}'.
                format(','.join(self.mimetypes_to_include, )),
                category='info',
            )

        """Prepare object property filter"""
        property_namespace = None
        property_attribute = None
        if self.filter_by_object_property:
            property_namespace, property_attribute = \
                ObjectProperty.Parse_Property_Name(
                    self.filter_by_object_property
                )
            self.log_message(
                'Will only include documents having a property of "{{{0}}}{1}"'
                .format(property_namespace, property_attribute, )
            )

        included_documents = list()
        for object_id in [x.assigned_id for x in collection.assignments]:
            document = self._ctx.r_c('document::get', id=object_id, )
            if not document:
                self.log_message(
                    'Unable to marshall OGo#{0} [Document] from collection.'
                    .format(document.object_id, )
                )
                continue
            if 'any' not in self.mimetypes_to_include:
                mimetype = self._ctx.type_manager.get_mimetype(document)
                if mimetype not in self.mimetypes_to_include:
                    self.log_message(
                        'OGo#{0} [Document] has incorrect MIME-type.'
                        .format(document.object_id, ),
                        category='debug',
                    )
                    continue
            if property_namespace and property_namespace:
                object_property = self._ctx.property_manager(
                    entity=document,
                    namespace=property_namespace,
                    attribute=property_attribute,
                )
                if not object_property:
                    self.log_message(
                        'OGo#{0} [Document] lacks required property.'
                        .format(document.object_id, ),
                        category='debug',
                    )
                    continue
            self.log_message(
                'OGo#{0} [Document] to be included in archive.'
                .format(document.object_id, ),
                category='debug',
            )
            included_documents.append(document)

            if (
                self.document_limit > 0 and
                len(included_documents) > self.document_limit
            ):
                self.log_message(
                    'Maximum number of documents included in archive.',
                    category='debug',
                )
                break

        # Create the ZipFile object on the actions' write file handle
        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )

        scrubbrush = ScrubBrush(self)
        if not self._enable_scrubbrush:
            scrubbrush.disable()
        for document in included_documents:
            sfile = scrubbrush.scrub(document)
            zfile.write(sfile.name, arcname=document.get_file_name(), )
            BLOBManager.Close(sfile)
            self.log_message(
                'OGo#{0} [Document] appended to ZIP file'
                .format(document.object_id, ),
                category='info',
            )
        scrubbrush.close()

        if included_documents and self._include_manifest:
            """
            Generate a manifest.xml file into the archive containing
            information relating to the documents within the archive.
            """
            scratch = BLOBManager.ScratchFile(require_named_file=True, )
            self.generate_manifest(
                documents=included_documents, wfile=scratch,
            )
            scratch.seek(0)
            zfile.write(
                scratch.name,
                arcname='metadata.xml',
            )
            BLOBManager.Close(scratch)
            self.log_message(
                'manifest.xml file generated into archive for {0} documents'
                .format(len(included_documents), ),
                category='info',
            )

        # Add the content from the message handle
        zfile.close()
        self.wfile.flush()

        if len(included_documents) == 0 and self._fail_if_no_candidates:
            raise CoilsException(
                'FolderToZIPFileAction refusing to create an empty ZIP archive'
            )

        if self.unassign_included_documents:
            for document in included_documents:
                self.log_message(
                    'Unassigning OGo#{0} [Document] from collection'
                    .format(document.object_id, ),
                    category='debug',
                )
                self._ctx.run_command(
                    'collection::delete-assignment',
                    collection=collection,
                    entity=document,
                )

    def parse_action_parameters(self):

        self._project_uri = self.action_parameters.get('projectPath', '')
        if not self._project_uri:
            raise CoilsException(
                'No projectPath specified in folderToZipFile'
            )
        self._project_uri = self.process_label_substitutions(self._project_uri)

        '''
        If failIfEmpty==YES and no documents are included in the ZIP
        archive the action should fail with an exception,  otherwise an
        empty ZIP archive may be created
        '''
        self._fail_if_no_candidates = \
            True if self.process_label_substitutions(
                self.action_parameters.get('failIfEmpty', 'NO')
            ).upper() == 'YES' else False

        self._include_manifest = \
            True if self.process_label_substitutions(
                self.action_parameters.get('includeManifest', 'NO')
            ).upper() == 'YES' else False

        self._enable_scrubbrush = \
            True if self.process_label_substitutions(
                self.action_parameters.get('enableScrubBrush', 'NO')
            ).upper() == 'YES' else False

        mimetypes = self.action_parameters.get('mimeTypes', 'any')
        mimetypes = self.process_label_substitutions(mimetypes)
        mimetypes = [x.strip() for x in mimetypes.split(',')]
        self.mimetypes_to_include = mimetypes

        self.filter_by_object_property = self.process_label_substitutions(
            self.action_parameters.get('requiredObjectProperty', None)
        )

        self.document_limit = self.process_label_substitutions(
            self.action_parameters.get('documentCountLimit', '-1')
        )
        self.document_limit = int(self.document_limit)

        self.unassign_included_documents = False
        purge_flag = self.process_label_substitutions(
            self.action_parameters.get('unassignIncludedDocuments', 'NO')
        )
        if purge_flag.upper() == 'YES':
            self.unassign_included_documents = True

    def do_epilogue(self):
        pass
