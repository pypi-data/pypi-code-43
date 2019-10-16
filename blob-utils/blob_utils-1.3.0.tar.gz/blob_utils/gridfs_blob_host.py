"""GridFS Blob Host
"""


import gridfs
from bson.objectid import ObjectId
from pymongo import MongoClient

from blob_utils.blob_host import BLOBHost
from blob_utils.commons.exceptions import BLOBError

CONNECTION_TIMEOUT = 100


class GridFSBLOBHost(BLOBHost):
    def __init__(self, blob_host_uri):
        """Initializes GridFS blob host

        Args:
            blob_host_uri: MongoDB uri (mongodb://username:password@host:port/database)
        """
        BLOBHost.__init__(self, blob_host_uri)

        try:
            # connect to mongo instance
            self.client = MongoClient(self.blob_host_uri,
                                      serverSelectionTimeoutMS=CONNECTION_TIMEOUT)
            # check connection
            self.client.server_info()
            # get database name from uri
            database_name = blob_host_uri.split('/')[-1]
            # connect to database
            self.database = self.client[database_name]
            # connect to gridfs
            self.fs = gridfs.GridFS(self.database)
        except:
            raise BLOBError("Unable to create the connection to the GridFS collection.")

    def get(self, handle):
        """Returns a blob

        Args:
            handle: blob id

        Returns:

        """
        try:
            if self.fs.exists(ObjectId(handle)):
                with self.fs.get(ObjectId(handle)) as blob:
                    return blob.read()
            else:
                raise BLOBError('No file found for the given id.')
        except:
            raise BLOBError('An unexpected error occurred while retrieving the file.')

    def list(self):
        """Returns list of blob ids

        Returns:

        """
        return [str(blob._id) for blob in self.fs.find()]

    def save(self, blob, filename=None, metadata=None):
        """Saves a blob

        Args:
            blob:
            filename:
            metadata:

        Returns:

        """
        try:
            if metadata is None:
                metadata = dict()
            blob_id = self.fs.put(blob, filename=filename, metadata=metadata)
        except Exception as e:
            raise BLOBError("An error occurred while saving the file.")
        return blob_id

    def delete(self, handle):
        """Deletes a blob

        Args:
            handle: blob id

        Returns:

        """
        try:
            if self.fs.exists(ObjectId(handle)):
                self.fs.delete(ObjectId(handle))
        except:
            raise BLOBError("An error occurred while deleting the file.")

    def query(self, query):
        """Query the blob collection - not implemented

        Args:
            query:

        Returns:

        """
        BLOBHost.query(self)
