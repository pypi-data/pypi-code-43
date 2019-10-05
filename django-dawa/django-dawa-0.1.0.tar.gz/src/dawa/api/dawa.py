import requests
import logging

logger = logging.getLogger('django_dawa.%s' % __name__)

class DAWA:
    def request(self, url, params=None):
        # force HTTPS (dawa api returns http:// href attributes)
        if url[:5] == "http:":
            url = url.replace("http://", "https://")

        # make the request
        try:
            r = requests.get(url, params=params)
        except requests.exceptions.RequestException as E:
            logger.exception(
                "Got exception while making dawa request for %s" % url
            )
            return False

        # check status code
        if r.status_code != 200:
            logger.error("Got status_code %s from dawa url %s" % (
                r.status_code,
                url
            ))
            return False

        # return the result
        return r.json()

    def _vask(self, entitet, betegnelse):
        url = 'http://dawa.aws.dk/datavask/%s' % entitet
        return self.request(
            url=url,
            params={
                'betegnelse': betegnelse
            }
        )

    def adresse_vask(self, betegnelse):
        return self._vask("adresser", betegnelse)

    def adgangadresse_vask(self, betegnelse):
        return self._vask("adgangsadresser", betegnelse)

    def adresser(self, uuid):
        url = 'http://dawa.aws.dk/adresser'
        return self.request(
            url=url,
            params={
                'id': uuid,
            }
        )

