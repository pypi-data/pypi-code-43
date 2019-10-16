import requests


class MockResponse(requests.Response):
    text = ""

    def __init__(self, text):
        super().__init__()
        self.text = text
