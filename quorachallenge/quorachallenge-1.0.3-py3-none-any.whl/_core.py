import json
import pathlib
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Union
import docutils.core
import requests
import io


class FileResponse:
    """Fake Requests like response object for a file."""

    def __init__(self, text):
        self._text = text

    @property
    def text(self):
        """The text property of the response - (the contents of the file)"""
        return self._text

    def json(self):
        """The json interpretation of the file"""
        d = json.loads(self.text)
        return d


class Challenge:
    def __init__(self, challenge_name: str, _directory: str = None):
        self._challenge_name = challenge_name
        self._base_dir = _directory

    @property
    def name(self):
        return self._challenge_name

    @property
    def basedir(self):
        return self._base_dir

    @staticmethod
    def _load_in_default_browser(html: str) -> None:
        """Display html in the default web browser without creating a temp file.

        Instantiates a trivial http server and calls webbrowser.open with a URL
        to retrieve html from that server.
        """

        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(html))
                self.send_header('Content-Encoding', 'utf-8')
                self.end_headers()
                self.wfile.write(b'<!DOCTYPE html>')
                self.wfile.write(b'<meta charset="utf-8">')
                buffer_size = 1024 * 1024
                for i in range(0, len(html), buffer_size):
                    self.wfile.write(html[i:i + buffer_size])

        server = HTTPServer(('127.0.0.1', 8080), RequestHandler)
        webbrowser.open('http://127.0.0.1:%s' % server.server_port)
        server.handle_request()

    def __build_url(self, item: str) -> str:
        return f'https://raw.githubusercontent.com/TonyFlury/QuoraChallengesTestData/master/' \
               f'{self._challenge_name}/{item}'

    def fetch(self, item: str, optional: bool = False) -> Union[requests.Response, FileResponse, None]:
        """Simple fetch of a resource from a given name and item"

            :param str item : The item to be fetched
            :param bool optional : Whether the item is optional or not
                                   if optional is True then a 404 error generates a None return value
                                   if optional is False then a 404 error results in a Value Error
        """
        if not self._base_dir:
            url = self.__build_url(item)
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.HTTPError:
                if not optional:
                    raise ValueError(
                        f"Unable to find information for '{self._challenge_name}' : Is the name correct ?") from None
                else:
                    return None
            except requests.exceptions.RequestException as exc:
                raise exc from None
        else:
            try:
                response = FileResponse(pathlib.Path(self._base_dir, self._challenge_name, item).read_text())
            except FileNotFoundError:
                if not optional:
                    raise ValueError(
                        f"Unable to find information for '{self._challenge_name}' : Is the name correct ?") from None
                else:
                    return None

        return response

    def testdata(self, test_id: str = None):
        """Display the test data for the given challenge

          :param str test_id: The test test_id. If left as the default value this function will display the data for
                all of the test cases.
                If it is not None, then this function will display the data for the test case with that test_id

        *In normal use the test data is downloaded from a remote site, so this function requires an active public
        internet connection.*
       """
        with io.StringIO() as stream:
            _data = self.fetch(item='testdata.json').json()
            for index, row in enumerate(_data):
                this_id = row.get('test_id', str(index))
                if test_id is not None and test_id != this_id:
                    continue
                row['test_id'] = this_id
                stream.write(f'------\n')
                stream.write(f'Id : {row["test_id"]}\n')
                stream.write(f'Called as : your_function({row["arguments"]})\n')
                if 'raises' in row:
                    stream.write(f'Expected to raise : {row["raises"]}\n')
                else:
                    stream.write(f'Expected to return : {row["return"]}\n')

            test_data_formatted = stream.getvalue()

        return test_data_formatted

    def describe(self, webpage: bool = True, _directory: str = None):
        """Describe the specified challenge.
            By default this function will open a web-browser and display the description of the challenge.

            :param bool webpage: When True the function will display the description in a web browser
                in a new tab or windows. When False the function will return the description in `rst`_ format.
            :param str _directory: The base local directory to search for this challenge in. Implemented to allow
                testing of challenges before publication. For Contributor use only.

            *In normal use the description is downloaded from a remote site, so this function requires an active public
            internet connection.*
        """
        response = self.fetch('description.rst')

        if webpage:
            html = docutils.core.publish_string(source=response.text, writer_name="html")
            self._load_in_default_browser(html=html)
        else:
            return response
