from PyVoice.MyDict import MyDict, DictProperty


class LatLng(MyDict):
    """
    {
      "latitude": number,
      "longitude": number
    }
    """
    latitude: float = DictProperty('latitude', float)
    longitude: float = DictProperty('longitude', float)

    def build(self, latitude:float, longitude:float):
        self.latitude = latitude
        self.longitude = longitude

        return self
