from uuid import uuid4

from honeycomb.models import Query, Mutation, DatapointInput, Datapoint
from gqlpycgen.client import FileUpload, Client


class HoneycombClient:

    def __init__(self, uri=None, accessToken=None, client_credentials=None):
        self.uri = uri
        if self.uri is None:
            self.uri = "https://honeycomb.apparatus.wildflowertesting.org/graphql"
        self.accessToken = accessToken
        self.client_credentials = client_credentials
        assert self.accessToken is not None or self.client_credentials is not None
        self.client = Client(self.uri, self.accessToken, self.client_credentials)
        self.mutation = HoneycombMutation(self.client)
        self.query = HoneycombQuery(self.client)

    def raw_query(self, query, variables):
        return self.query.query(query, variables)


class HoneycombQuery(Query):
    pass


class HoneycombMutation(Mutation):

    def createDatapoint(self, datapoint: DatapointInput) -> Datapoint:
        variables = dict()

        if datapoint is None:
            raise Exception("datapoint is required")

        query = """mutation createDatapoint ($datapoint: DatapointInput) { createDatapoint(datapoint: $datapoint) {
    data_id
        format
        file {
            name
            filename
            mime
            encoding
            contentType
            size
            created
        }
        timestamp
        system {
            type_name
            created
            last_modified
        }
    }
}
"""
        files = FileUpload()
        upload = datapoint.file
        data = upload.data
        filename = uuid4().hex
        upload.data = filename
        files.add_file("variables.datapoint.file.data", filename, data, upload.contentType)
        if hasattr(datapoint, "to_json"):
            variables["datapoint"] = datapoint.to_json()
        else:
            variables["datapoint"] = datapoint
        results = self.client.execute(query, variables, files)
        if hasattr(results, "get"):
            return Datapoint.from_json(results.get("createDatapoint"))
        else:
            print(results)
            raise Exception("createDatapoint failed")
