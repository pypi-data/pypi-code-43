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
    def get(self) -> list:
        log.info('Scraping pages')
        self.data: list = []
        for scraper in scrapers:
            self.data.append(scraper.scrape())  # type: ignore
        return self.data

    def save(self, path: Union[Path, str], recursive_concepts: bool = True, **kwargs: Any) -> None:
        log.info('Creating datapackage')
        path = Path(path)
        packages: list = []

        for i, data in enumerate(self.data):
            package = DataPackage(data['data'])
            if data['datapoints']:
                package.set_datapoints(*data['datapoints'])
            packages.append(package)

        merge_packages(packages, path, **kwargs)
        log.info('Datapackage successfully created')
