class PreSignedUrlContract:
    url = ""
    timestamp = ""
    fileName = ""

    def __init__(self, url, timestamp, file_name):
        self.url = url
        self.timestamp = timestamp
        self.fileName = file_name