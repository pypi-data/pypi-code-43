from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .LatLng import LatLng
from .PostalAddress import PostalAddress


class Location(MyDict):
    """
    {
      "coordinates": {
        object(LatLng)
      },
      "formattedAddress": string,
      "zipCode": string,
      "city": string,
      "postalAddress": {
        object(PostalAddress)
      },
      "name": string,
      "phoneNumber": string,
      "notes": string,
      "placeId": string
    }
    """
    coordinates: LatLng = DictProperty('coordinates', LatLng)
    formatted_address: str = DictProperty('formattedAddress', str)
    zip_code: str = DictProperty('zipCode', str)
    city: str = DictProperty('city', str)
    postal_address: PostalAddress = DictProperty('postalAddress', PostalAddress)
    name: str = DictProperty('name', str)
    phone_number: str = DictProperty('phoneNumber', str)
    notes: str = DictProperty('notes', str)
    place_id: str = DictProperty('placeId', str)

    def build(self, coordinates: LatLng=None, formatted_address: str=None, zip_code:str=None, city:str=None,
              postal_address:str = None, name:str = None, phone_number: str = None, notes:str = None,
              place_id: str =None):

        if coordinates is not None:
            self.coordinates = coordinates

        if formatted_address is not None:
            self.formatted_address = formatted_address

        if zip_code is not None:
            self.zip_code = zip_code

        if city is not None:
            self.city = city

        if postal_address is not None:
            self.postal_address = postal_address

        if name is not None:
            self.name = name

        if phone_number is not None:
            self.phone_number = phone_number

        if notes is not None:
            self.notes = notes

        if place_id is not None:
            self.place_id = place_id

    def add_latlng(self, latitude: float, longitude: float) -> LatLng:
        self.coordinates = LatLng().build(latitude=latitude, longitude=longitude)
        return self.coordinates

    def add_postal_address(self, revision:int=None, region_code:str=None, language_code:str=None, postal_code:str=None,
              sorting_code:str=None, administrative_area:str=None, locality:str=None, sublocality:str=None,
              address_lines: List[str]=None, recipients: List[str]=None, organization:str=None) -> PostalAddress:

        self.postal_address = PostalAddress().build(revision, region_code, language_code, postal_code, sorting_code,
                                                    administrative_area, locality, sublocality, address_lines,
                                                    recipients, organization)

        return self.postal_address