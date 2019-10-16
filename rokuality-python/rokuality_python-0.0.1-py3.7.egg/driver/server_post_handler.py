from src.httpexecutor.http_client import HttpClient

class ServerPostHandler:

    httpClient = None

    def __init__(self, httpClient):
        self.httpClient = httpClient

    def postToServerWithHandling(self, servletName, requestJSON, exception):
        resultJSON = self.httpClient.postToServer(servletName, requestJSON)
        if not resultJSON['results'] == 'success':
            raise exception(resultJSON['results'])
