import requests


class Client(object):
    def __init__(self, namespace, token, endpoint="https://av-upload.bmat.com/api/files"):
        self.namespace = namespace
        self.token = token
        self.endpoint = endpoint
        self.headers = {
            'authorization': "Bearer " + token,
        }

        self.params = {
            "namespace": namespace
        }

    def put(self, file):
        files = {'file': file}
        return requests.post(self.endpoint, files=files, data=self.params, headers=self.headers).json()['id']

    def get(self, file_id):
        return requests.get("{endpoint}/{file_id}".format(
            endpoint=self.endpoint,
            file_id=file_id
        ), data=self.params, headers=self.headers).json()

    def list(self, page=1, page_size=10):
        return requests.get(
            "{endpoint}?page={page}&pageSize={page_size}".format(
                endpoint=self.endpoint,
                page=page,
                page_size=page_size
            ), data=self.params, headers=self.headers).json()

    def delete(self, file_id):
        r = requests.delete("{endpoint}/{file_id}".format(
            endpoint=self.endpoint,
            file_id=file_id
        ), data=self.params, headers=self.headers)
        return r.status_code == 200

    def download(self, file_id):
        r = requests.get("{endpoint}/{file_id}/download".format(
            endpoint=self.endpoint,
            file_id=file_id
        ), data=self.params, headers=self.headers)
        return r.content
