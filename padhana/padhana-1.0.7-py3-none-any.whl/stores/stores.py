import base64
import json
from padhana.core import Document, DocumentMetadata, ContentNode
from pathlib import Path


class JsonDocumentStore:
    """
    An implementation of a document store that is in-memory and uses a JSON file for persistence
    """

    def __init__(self, file_path):
        self.file_path = file_path
        path = Path(file_path)
        self.documents = []
        if path.is_file():
                self.__read()

    def count(self):
        """
        The number of documents in the store

        :return: The number of documents
        """
        return len(self.documents)

    def get(self, idx):
        """
        Load the document at the given index

        :return: Document at given index
        """
        return self.documents[idx]

    def save(self, idx, document):
        """
        Save the document at the given index

        :return: Document at given index
        """
        self.documents[idx] = document
        return document

    def delete(self, idx):
        """
        Delete the document at the given index

        :return: The Document that was removed
        """
        return self.documents.pop(idx)

    def add(self, document):
        """
        Add a new document and return the index position

        :return: The index of the document added
        """
        self.documents.append(document)
        return len(self.documents)

    def __write(self):
        """
        Private method to write the JSON store back to disk
        """

    def __read(self):
        """
        Private method to read the JSON store back into in-memory from disk
        """
        with open(self.file_path) as f:
            self.raw_lines = f.readlines()

        for raw_line in self.raw_lines:
            serialized_document = json.loads(raw_line)
            metadata = DocumentMetadata(json.loads(base64.standard_b64decode(serialized_document['metadata'])))
            content = ContentNode(json.loads(base64.standard_b64decode(serialized_document['metadata'])))
            self.documents.append(Document(metadata, content))


