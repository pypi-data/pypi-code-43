from PyVoice.MyDict import MyDict, DictProperty
from .DateTime import DateTime
from .Extension import Extension
from .Status import Status
from .Location import Location
from .LatLng import LatLng


class Argument(MyDict):
    """
    {
      "name": string,
      "rawText": string,
      "textValue": string,
      "status": {
        object(Status)
      },

      // Union field value can be only one of the following:
      "intValue": string,
      "floatValue": number,
      "boolValue": boolean,
      "datetimeValue": {
        object(DateTime)
      },
      "placeValue": {
        object(Location)
      },
      "extension": {
        "@type": string,
        field1: ...,
        ...
      },
      "structuredValue": {
        object
      }
      // End of list of possible types for union field value.
    }
    """

    #TODO Argument object needs to be completed.
    name: str = DictProperty('name', str)
    raw_text: str = DictProperty('rawText', str)
    text_value: str = DictProperty('textValue', str)
    status: Status = DictProperty('status', Status)
    int_value:str = DictProperty('intValue', str)
    float_value: int = DictProperty('floatValue', int)
    bool_value: bool = DictProperty('boolValue', bool)
    datetime_value: DateTime = DictProperty('datetimeValue', DateTime)
    place_value: Location = DictProperty('placeValue', Location)
    extension: Extension = DictProperty('extension', Extension)
    structured_value: dict = DictProperty('structuredValue', dict)

    def build(self, name:str=None, raw_text:str=None, text_value: str=None, status:Status=None, int_value:str=None,
              float_value:str=None, bool_value:bool=False, datetime_value:str=None, place_value: Location=None,
              extension:Extension=None, **structure_values):
        if name is not None:
            self.name = name
        if raw_text is not None:
            self.raw_text = raw_text
        if text_value is not None:
            self.text_value = text_value
        if status is not None:
            self.status = status
        if int_value is not None:
            self.int_value = int_value
        if float_value is not None:
            self.float_value = float_value
        if bool_value is not None:
            self.bool_value = bool_value
        if datetime_value is not None:
            self.datetime_value = datetime_value
        if place_value is not None:
            self.place_value = place_value
        if extension is not None:
            self.extension = extension
        if structure_values is not None:
            self.structured_value = structure_values

        return self

    def add_status(self, code: int, message:str, type:str, **fields) -> Status:
        self.status = Status().build(code=code, message=message, type=type, **fields)
        return self.status

    def add_datetimevalue(self, date:str, time:str) -> DateTime:
        self.datetime_value = DateTime().build(date=date, time=time)
        return self.datetime_value

    def add_place_value(self, coordinates: LatLng=None, formatted_address: str=None, zip_code:str=None, city:str=None,
              postal_address:str = None, name:str = None, phone_number: str = None, notes:str = None,
              place_id: str =None) -> Location:
        self.place_value = Location().build(coordinates=coordinates, formatted_address=formatted_address,
                                            zip_code=zip_code, city=city, postal_address=postal_address,name=name,
                                            phone_number=phone_number, notes=notes, place_id=place_id)
        return self.place_value

    def add_extension(self, type: str, **kwargs) -> Extension:
        self.extension = Extension().build(type, **kwargs)
        return self.extension

    def add_structure(self, **kwargs) -> dict:
        self.structured_value = kwargs
        return self.structured_value
