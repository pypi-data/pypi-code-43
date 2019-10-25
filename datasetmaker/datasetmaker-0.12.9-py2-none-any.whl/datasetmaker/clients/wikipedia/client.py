import logging
from typing import Union, Any
from pathlib import Path
from datasetmaker.datapackage import DataPackage
from datasetmaker.merge import merge_packages
from datasetmaker.models import Client
from . import election_scraper, leader_scraper, visa_scraper

log = logging.getLogger(__name__)

scrapers = [election_scraper, leader_scraper, visa_scraper]


class WikipediaClient(Client):
    def get(self, **kwargs: Any) -> list:
        log.info('Scraping pages')
        self.data: list = []
        for scraper in scrapers:
            self.data.append(scraper.scrape())  # type: ignore
        return self.data

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:
        log.info('Creating datapackage')

        kwargs.update({
            'author': 'Datastory',
            'default_measure': 'visa_requirement',
            'default_primary_key': ['country_flow.country_from', 'country_flow.country_to'],
            'name': 'wikipedia',
            'source': 'Wikipedia',
            'status': 'draft',
            'title': 'Wikipedia',
            'topics': [],
        })

        path = Path(path)
        packages = [DataPackage(x) for x in self.data]

        merge_packages(packages, path, **kwargs)
        log.info('Datapackage successfully created')
