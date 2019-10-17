import requests

from ..exceptions import NoInternetConnection
from .file import File


class Download:
    def __init__(self, url, verify_certificate=True):
        if not isinstance(url, str):
            raise TypeError(f"<url> must be {str}, {type(url)} given.")

        if not isinstance(verify_certificate, bool):
            raise TypeError(
                f"<verify_certificate> must be {bool}, {type(verify_certificate)} given."
            )

        self.url = url
        self.certificate_verification = verify_certificate

    def text(self, destination=None):
        try:
            req = requests.get(self.url, verify=self.certificate_verification)

            if req.status_code == 200:
                response = req.text

                if destination and isinstance(destination, str):
                    File(destination).write(req.text)

                return response

            raise Exception(
                f"Unable to download {req.url} (status code: {req.status_code})."
            )
        except requests.exceptions.ConnectionError:
            raise NoInternetConnection()
