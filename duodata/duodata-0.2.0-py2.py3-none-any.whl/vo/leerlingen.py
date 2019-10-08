from bs4 import BeautifulSoup
import pandas as pd
import requests
from duodata.algemeen import generieke_kolomnamen

url = 'https://duodata.nl/open_onderwijsdata/databestanden/vo/leerlingen/leerlingen-vo-7.jsp'


def target_urls(url=url):
    """Lijst met urls naar xlsx bestanden."""
    response = requests.get(url)
    # parse html
    page = str(BeautifulSoup(response.content))

    links = []
    soup = BeautifulSoup(page, 'lxml')
    for tag in soup.find_all('a', href=True):
        links.append(tag['href'])
    result = [link for link in links if link.endswith('.xlsx')]
    return result


def jaar_cijfers(asset_url, base_url='https://duodata.nl'):
    """Lees excel in in dataframe, voeg Afstudeerjaar toe op basis van
    collegejaar in url."""
    url = base_url + asset_url
    result = pd.read_excel(url)
    result['Afstudeerjaar'] = url[1][61:-10]
    return result


def cijfers_alle_jaren():
    """Alle cijfers van de beschikbare jaren."""
    result = []
    urls = target_urls()

    for url in urls:
        data = jaar_cijfers(url)
        result.append(data)
    total = pd.concat(result)
    total = total.rename(columns=generieke_kolomnamen)
    return total
