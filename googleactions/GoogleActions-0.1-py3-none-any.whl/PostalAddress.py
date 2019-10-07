from typing import List
from PyVoice.MyDict import MyDict, DictProperty


class PostalAddress(MyDict):
    """
    {
      "revision": number,
      "regionCode": string,
      "languageCode": string,
      "postalCode": string,
      "sortingCode": string,
      "administrativeArea": string,
      "locality": string,
      "sublocality": string,
      "addressLines": [
        string
      ],
      "recipients": [
        string
      ],
      "organization": string
    }
    """
    revision: int = DictProperty('revision', int)
    region_code: str = DictProperty('regionCode', str)
    language_code: str = DictProperty('languageCode', str)
    postal_code: str= DictProperty('postalCode', str)
    sorting_code: str = DictProperty('sortingCode', str)
    administrative_area: str = DictProperty('administrativeArea', str)
    locality: str = DictProperty('locality', str)
    sublocality: str = DictProperty('sublocality', str)
    address_lines: List[str] = DictProperty('addressLines', list)
    recipients: List[str] = DictProperty('recipients', list)
    organization: str = DictProperty('organization', str)

    def build(self, revision:int=None, region_code:str=None, language_code:str=None, postal_code:str=None,
              sorting_code:str=None, administrative_area:str=None, locality:str=None, sublocality:str=None,
              address_lines: List[str]=None, recipients: List[str]=None, organization:str=None):
        if revision is not None:
            self.revision = revision

        if region_code is not None:
            self.region_code = region_code

        if language_code is not None:
            self.language_code = language_code

        if postal_code is not None:
            self.postal_code = postal_code

        if sorting_code is not None:
            self.sorting_code = sorting_code

        if administrative_area is not None:
            self.administrative_area = administrative_area

        if locality is not None:
            self.locality = locality

        if sublocality is not None:
            self.sublocality = sublocality

        if address_lines is not None:
            self.address_lines = address_lines

        if recipients is not None:
            self.recipients = recipients

        if organization is not None:
            self.organization = organization

        return self

    def add_address_lines(self, *address_lines: str) -> List[str]:
        for item in address_lines:
            assert isinstance(item, str)
            self.address_lines.append(item)

        return self.address_lines

    def add_recipients(self, *recipients: str) -> List[str]:

        for item in recipients:
            assert isinstance(item, str)
            self.recipients.append(item)

        return self.recipients