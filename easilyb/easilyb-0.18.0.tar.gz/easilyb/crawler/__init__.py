from easilyb.urlselector import  UrlSelector
from easilyb.net.requestqueue import Requester
from lxml.html import fromstring
import logging
logger = logging.getLogger(__name__)



def _crawler_callback(resp, index=None):
    url,counter, depth, crawler = index
    crawler._parse_response(url, depth, resp)


class LxmlXpathLinkExtractor:
    def __init__(self):
        pass
    def extract_links(self, baseurl, response):
        html = fromstring(response, base_url=baseurl)
        html.make_links_absolute()
        return html.xpath('//a/@href')

class Crawler:
    def __init__(self, baseurls, callback, urlselector=None, urlextractor=None, maxdepth=3, maxurls=100, threads=4):
        self.baseurls = baseurls
        self.callback = callback
        self._urlselector = urlselector or UrlSelector()
        self._urlextractor = urlextractor or LxmlXpathLinkExtractor()
        self.maxdepth = maxdepth
        self.maxurls = maxurls #TODO: can't with the current workerqueue or urlselector implementation
        self._urlselector.limit = maxurls #TODO: may be dangerous
        self._threads = threads
        self._requester = Requester(threads=self._threads, queue=self._urlselector)
        self._counter = 0
        for u in self.baseurls:
            index = (u,self._counter,  0, self,)
            self._requester.get(_crawler_callback, u, index)
            self._counter+=1

    def _parse_response(self, url, depth, response):
        self.callback(url, response)
        if depth + 1 < self.maxdepth:
            logger.debug('Parsing response for url=%s', url)
            links = self._urlextractor.extract_links(url, response.text)
            for u in links:
                logger.debug("Found link: %s", u)
                index = (u,self._counter,  depth + 1, self,)
                self._requester.get( _crawler_callback, u, index)
                self._counter+=1

    def join(self):
        self._requester.join()







