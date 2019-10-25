#
# Copyright (c) 2015, 2016, 2017
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
from coils.core import BLOBManager, CoilsException, PropertyManager
from coils.core.logic import ActionCommand
from command import DocumentBaseAction
from coils.foundation import qsearch_from_xml
from scrubbrush import ScrubBrush


class SearchDocumentsToZIPFileAction(ActionCommand, DocumentBaseAction):
    """
    Archive the contents of a document folder into a ZIP file
    """
    __domain__ = "action"
    __operation__ = "search-documents-to-zipfile"
    __aliases__ = [
        'searchDocumentsToZipFile', 'searchDocumentsToZipFileAction',
    ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def get_file_name(self, document):
        """
        Support renaming of documents as they are stored in the ZIP file.
        First support naming transform is to use the string value of an
        object property as the filename; this is assume if the rename_pattern
        begins with the character "{"
        If anything goes wrong we fall back to the default document file name.
        """
        if not self._rename_pattern:
            return document.get_file_name()
        if self._rename_pattern.startswith('{'):
            try:
                namespace, attribute = \
                    PropertyManager.Parse_Property_Name(self._rename_pattern)
                prop = self._ctx.property_manager.get_property(
                    document, namespace, attribute,
                )
                if not prop:
                    return document.get_file_name()
                if not prop.get_string_value():
                    return document.get_file_name()
                if document.extension:
                    return '{0}.{1}'.format(
                        prop.get_string_value(), document.extension,
                    )
                else:
                    return prop.get_string_value()
            except Exception:
                return document.get_file_name()
        return document.get_file_name()

    def do_action(self):

        uncollection = None  # Collection we will unassigned from, if not None
        if self._uncollection_name:
            uncollection = self._marshall_collection(
                collection_name=self._uncollection_name,
                collection_kind=self._uncollection_kind,
                create=False,
            )
            if not uncollection:
                raise CoilsException(
                    'Unable to marshall collection named "{0}" of kind "{1}" '
                    'for uncollection of document search result.'
                    .format(self._uncollection_name, self._uncollection_kind, )
                )
            self.log_message(
                'Marshalled OGo#{0} [Collection] named "{1}" for uncollection '
                'of search results'
                .format(uncollection.object_id, uncollection.title, ),
                category='debug',
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
            'Retrieved {0} documents via document search.'
            .format(len(documents), ),
            category='debug',
        )

        # Create the ZipFile object on the actions' write file handle
        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )

        max_object_id = 0

        scrubbrush = ScrubBrush(self)
        if not self._enable_scrubbrush:
            scrubbrush.disable()
        for document in documents:
            sfile = scrubbrush.scrub(document)
            filename = self.get_file_name(document)
            zfile.write(sfile.name, arcname=filename, )
            BLOBManager.Close(sfile)
            self.log_message(
                'OGo#{0} "{1}" [Document] appended to ZIP file'
                .format(document.object_id, filename, ),
                category='info',
            )
            if document.object_id > max_object_id:
                max_object_id = document.object_id
        scrubbrush.close()

        if documents and self._include_manifest:
            """
            Generate a manifest.xml file into the archive containing
            information relating to the documents within the archive.
            """
            scratch = BLOBManager.ScratchFile(require_named_file=True, )
            self.generate_manifest(
                documents=documents, wfile=scratch,
            )
            scratch.seek(0)
            zfile.write(scratch.name, arcname='metadata.xml', )
            BLOBManager.Close(scratch)
            self.log_message(
                'manifest.xml file generated into archive for {0} documents'
                .format(len(documents), ), category='info',
            )

        # Add the content from the message handle
        zfile.close()
        self.wfile.flush()

        if len(documents) == 0 and self._fail_if_no_candidates:
            raise CoilsException(
                'FolderToZIPFileAction refusing to create an empty ZIP archive'
            )

        self._ctx.property_manager.set_property(
            entity=self.process,
            namespace='57c7fc84-3cea-417d-af54-b659eb87a046',
            attribute='maximumDocumentId',
            value=max_object_id,
        )

        # we do not need to UNcollect documents that will be deleted
        if self._purge_included:
            for document in documents:
                self.log_message(
                    'Deleting included document OGo#{0}'
                    .format(document.object_id, ),
                    category='debug',
                )
                self._ctx.run_command(
                    'document::delete', object=document,
                )
        elif uncollection:
            for document in documents:
                self.log_message(
                    'Unassigning OGo#{0} [Document] from collection'
                    .format(document.object_id, ),
                    category='debug',
                )
                self._ctx.run_command(
                    'collection::delete-assignment',
                    collection=uncollection,
                    entity=document,
                )

    def parse_action_parameters(self):

        qsearch_text = self.action_parameters.get('qsearch', '')
        if not qsearch_text:
            raise CoilsException(
                'No qsearch criteria specified in '
                'searchDocumentsToZipFileAction'
            )
        self._qsearch_text = self.process_label_substitutions(qsearch_text)

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

        self._uncollection_name = \
            self.process_label_substitutions(
                self.action_parameters.get('uncollectionName', None)
            )
        if not self._uncollection_name:
            self._uncollection_name = None
        self._uncollection_kind = \
            self.process_label_substitutions(
                self.action_parameters.get('uncollectionKind', None)
            )
        if not self._uncollection_kind:
            self._uncollection_kind = None

        self._enable_scrubbrush = \
            True if self.process_label_substitutions(
                self.action_parameters.get('enableScrubBrush', 'NO')
            ).upper() == 'YES' else False

        self._purge_included = \
            True if self.process_label_substitutions(
                self.action_parameters.get('purgeIncludedDocuments', 'NO')
            ).upper() == 'YES' else False

        self._rename_pattern = self.process_label_substitutions(
            self.action_parameters.get('renameDocumentsAs', None)
        )

    def do_epilogue(self):
        pass
