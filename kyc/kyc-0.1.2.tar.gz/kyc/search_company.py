from kyc.connection import Connection
from kyc.util import Util
import pandas as pd

def search_company(keyword, rows=100):
    path = "search/company/%s" % (keyword)
    options={ 'params' :{"rows": rows}}
    r = Connection.request('get', path, **options)
    response_data = r.json()
    Util.convert_to_dates(response_data)
    
    return pd.DataFrame(response_data['searchResults'])