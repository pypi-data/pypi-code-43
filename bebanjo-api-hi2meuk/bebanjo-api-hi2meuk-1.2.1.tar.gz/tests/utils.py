import re
import xml.etree.ElementTree as ET  # nosec (trused XML source)
from bebanjo.things import objectify_element


def object_from_file(filename, res_name):
    with open(f'tests/__files/{filename}', 'rb') as file:
        et = ET.parse(file).getroot()
        url = f'http://localhost:8080/api{res_name}'
        obj = objectify_element(et, url)
    return obj


def titles_from_file(fn='titles_3pp_p1.xml', ):
    filename = 'tests/__files/' + fn
    with open(filename, 'rb') as file:
        et = ET.parse(file).getroot()
        url = 'http://localhost:8080/api/titles'
        obj = objectify_element(et, url)
    return obj


def assert_send_body_calls_match(mock, *, re_method=[], re_url=[], re_body=[]):
    if not mock.mock_calls:
        raise AssertionError('No urllib call made')
    for call in mock.mock_calls:
        url = call[1][0]
        method = call[2].get('method', '')
        body = call[2].get('data', b'').decode()
        for name, list_expected, actual in zip(
                'Method URL Body'.split(),
                (re_method, re_url, re_body),
                (method, url, body)
        ):
            if not isinstance(list_expected, list):
                list_expected = [list_expected]
            for expected in list_expected:
                if not re.search(expected, actual):
                    raise AssertionError(f'{name} should match regex {expected} \
                        actual value is {actual}')


class FileReader():

    def __init__(self, filename=None, response_code=200):
        self.response_code = response_code
        if filename:
            with open('tests/__files/' + filename, 'rb') as f:
                self.bstr = f.read()
            f.close()
        else:
            self.bstr = b'<root />'

    def read(self):
        return self.bstr

    def getcode(self):
        return self.response_code
