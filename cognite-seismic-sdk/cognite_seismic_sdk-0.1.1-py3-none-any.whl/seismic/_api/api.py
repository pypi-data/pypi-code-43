# Copyright 2019 Cognite AS

import os

if not os.getenv("READ_THE_DOCS"):
    import cognite.seismic.protos.types_pb2 as stypes


class API:
    def __init__(self, metadata, query=None, ingestion=None):
        self.query = query
        self.ingestion = ingestion
        self.metadata = metadata

    @staticmethod
    def identify(id=None, name=None):
        """
        Returns an identifier with filled with id or name. If both are filled, will prefer id.
        """
        if not id and not name:
            raise Exception("Either `name` or `id` needs to be specified")
        return stypes.Identifier(id=id) if id else stypes.Identifier(name=name)
