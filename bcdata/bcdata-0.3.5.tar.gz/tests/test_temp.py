from bcdata import wfs

AIRPORTS_KEY = 'bc-airports'


param_dict = wfs.define_request(
    'bc-airports',
    query="AIRPORT_NAME='Victoria International Airport'"
)