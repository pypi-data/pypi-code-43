import click
import requests
from bs4 import BeautifulSoup
from requests import codes

from website_worth.constants import SCRAPERS


class BaseConfigScraper(object):
    NAME = ''

    def get(self, url):
        """
        Get source of calculated site
        :return: string
        """
        raise NotImplementedError

    def scrape(self, content):
        """
        Get data of calculated site
        :return: dict
        """
        raise NotImplementedError

    def run(self, url):
        content = self.get(url)
        data = self.scrape(content)
        click.echo("=== Data of '{}'".format(url))
        click.echo("=== Using '{}' calculator".format(self.NAME))
        for name, value in data.items():
            click.echo(" - {}: {}".format(name, value))


class WebukaScraper(BaseConfigScraper):
    URL = "http://www.webuka.com/files/apps/worth/websiteworth.php"
    NAME = 'https://webuka.com'

    def get(self, url):
        req = requests.post(self.URL, data={
            "www": url
        })
        if req.status_code is codes.OK:
            return req.content
        else:
            req.raise_for_status()

    def scrape(self, content):
        data = dict()
        soup = BeautifulSoup(content, "html.parser")
        groups = soup.find_all("hgroup")
        for group in groups:
            name = group.find("h3").text
            value = group.find("p").text
            data[name] = value
        return data


def get_scraper(app_name):
    """
    Return scraper based on app name.
    :param app_name: String
    :return: parser object
    """
    app_parser_name = SCRAPERS[app_name]
    parser = [subcls for subcls in BaseConfigScraper.__subclasses__() if
              subcls.__name__ == app_parser_name][0]
    return parser()  # return scraper object instead of class
