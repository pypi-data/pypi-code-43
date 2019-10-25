from typing import Union, Any
from pathlib import Path
import lxml
import requests
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.datapackage import DataPackage
from datasetmaker.onto.manager import _map
from datasetmaker.merge import merge_packages


class UNSC(Client):
    url = 'https://scsanctions.un.org/resources/xml/en/consolidated.xml'

    def get(self, **kwargs: Any) -> list:
        r = requests.get(self.url)
        etree = lxml.etree.fromstring(bytes(r.text, encoding='utf8'))
        individuals = self._xml_to_frame(etree, 'INDIVIDUALS', 'INDIVIDUAL')
        entities = self._xml_to_frame(etree, 'ENTITIES', 'ENTITY')

        # These fields are all empty or irrelevant to us
        drop_cols_individuals = [
            'DESIGNATION',
            'INDIVIDUAL_ADDRESS',
            'INDIVIDUAL_ALIAS',
            'INDIVIDUAL_DATE_OF_BIRTH',
            'INDIVIDUAL_DOCUMENT',
            'INDIVIDUAL_PLACE_OF_BIRTH',
            'LAST_DAY_UPDATED',
            'LIST_TYPE',
            'NATIONALITY',
            'SORT_KEY',
            'SORT_KEY_LAST_MOD',
            'TITLE'
        ]

        individuals = individuals.drop(drop_cols_individuals, axis=1)

        drop_cols_entities = [
            'ENTITY_ADDRESS',
            'ENTITY_ALIAS',
            'LAST_DAY_UPDATED',
            'LIST_TYPE',
            'SORT_KEY',
            'SORT_KEY_LAST_MOD'
        ]

        entities = entities.drop(drop_cols_entities, axis=1)

        individuals.columns = [f'unsc_{x.lower()}' for x in individuals.columns]
        individuals = individuals.rename(columns={
            'unsc_gender': 'gender',
            'unsc_dataid': 'unsc_sanctioned_individual'})
        individuals.gender = individuals.gender.str.lower()
        entities.columns = [f'unsc_{x.lower()}' for x in entities.columns]
        entities = entities.rename(columns={'unsc_dataid': 'unsc_sanctioned_entity'})

        individuals.unsc_submitted_by = individuals.unsc_submitted_by.map(
            _map('country', 'name', 'country')
        )

        individuals_props = ['unsc_versionnum', 'unsc_first_name', 'unsc_second_name',
                             'unsc_third_name', 'unsc_fourth_name', 'unsc_un_list_type',
                             'unsc_reference_number', 'unsc_listed_on', 'unsc_comments1',
                             'unsc_name_original_script', 'gender', 'unsc_submitted_by']
        individuals.ddf.register_entity('unsc_sanctioned_individual', props=individuals_props)
        individuals.ddf.register_entity('gender')

        entities_props = ['unsc_versionnum', 'unsc_first_name', 'unsc_un_list_type',
                          'unsc_reference_number', 'unsc_listed_on', 'unsc_comments1',
                          'unsc_name_original_script', 'unsc_submitted_on']
        entities.ddf.register_entity('unsc_sanctioned_entity', props=entities_props)

        self.data = [individuals, entities]
        return self.data

    def _xml_to_frame(self,
                      etree: lxml.etree._Element,
                      rootname: str,
                      nodename: str) -> pd.DataFrame:
        nodes = etree.find(rootname).findall(nodename)
        data = []

        for node in nodes:
            entry = {}
            for prop in node.getchildren():
                entry[prop.tag] = prop.text
            data.append(entry)

        return pd.DataFrame(data)

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:

        kwargs.update({
            'author': 'Datastory',
            'name': 'united-nations-security-council',
            'source': 'United Nations Security Council',
            'status': 'draft',
            'title': 'United Nations Security Council',
            'topics': ['crime'],
        })

        packages = [DataPackage(x) for x in self.data]
        merge_packages(packages, path, **kwargs)
