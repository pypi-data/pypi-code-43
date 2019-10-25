import os
from chardet.universaldetector import UniversalDetector


class FileEncodingDetector(object):
    def __init__(self, file_path):
        if not os.path.isfile(file_path):
            raise OSError('File Not Found: {}'.format(file_path))
        self.path = file_path
        self.detector = UniversalDetector()
        self.result = self.detect()

    def detect(self):
        for line in open(self.path, 'rb'):
            self.detector.feed(line)
            if self.detector.done:
                break
        self.detector.close()
        return self.detector.result.get('encoding')
