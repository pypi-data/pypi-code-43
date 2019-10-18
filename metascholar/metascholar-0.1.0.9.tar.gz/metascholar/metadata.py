import pandas as pd 
from crossref.restful import Works 
from unidecode import unidecode
import re
from urllib.parse import urlparse, unquote, unquote_plus, parse_qsl, urlencode
import requests
import urllib.request as urllib
from fuzzywuzzy import fuzz

def get_DOI_from_URL(address):
    """
    input: 
        address: web address
    output: 
        DOI of the URL (if able to find)
        False: if unable to find the DOI
    """
    return _doi_retrieve(address)
    


def get_metadata_from_DOI(DOI):
    """
    input:
        DOI : DOI of the article
    output:
        metadata : dictionary containing the metadata of article  
        False: if unable to find the metadata
    """
    return _get_metadata(DOI)


def get_metadata_from_URL(address, search = True):
    """
    input:
        address : Address of the article
    output:
        metadata : dictionary containing the metadata of article  
        False: if unable to find the metadata
    """
    DOI = _doi_retrieve(address)
    if DOI != False:
        result = _get_metadata(DOI)
        if result != False:
            return result
        return False
    else:
        if 'openurl' in address:
            result = _get_metadata_from_openurl(address, search)
            return result
        return False


def _doi_retrieve(address):
    """
    input: 
        address: web address
    output: 
        DOI of the URL (if able to find)
        False: if unable to find the DOI
    """
    address = unquote(address).replace(" ","")
    doi_regex = r"^.*[/:=?](10.\d{4,9}/[-._;()/:a-zA-Z0-9]+).*$"
    result = re.search(doi_regex, address)
    if result: 
        return(result.group(1))
    return(False)


def _get_metadata_from_openurl(url,search):
    """
    input:
        url: URL with a openurl
        search:
    output:
        metadata
        False: if unable to find the DOI or metadata
    """
    works = Works()
    url_infor = _openurl_direct_information(url)
    if search:
        title = url_infor.get("atitle")
        aufirst = url_infor.get("aufirst")  
        aulast = url_infor.get("aulast" )
        if title and (aufirst or aulast):
            author = aufirst + " " + aulast
            cross_url = works.query(bibliographic=title).query(author=author).url
            req = requests.get(url = cross_url)
            data_items = req.json()["message"]["items"]
            flag = 0
            for data_item in data_items:
                percent_comp = fuzz.partial_ratio(data_item["title"][0].lower(),url_infor["atitle"].lower())
                if percent_comp >= 95:
                    flag = 1
                    break
            if flag == 0:
                return url_infor
            DOI =  data_item.get("DOI")
            if DOI:
                return _get_metadata(DOI)
    return(url_infor)


def _get_metadata(DOI):
    """
    input:
        DOI : DOI of the article
    output:
        metadata : dictionary containing the metadata of article  
    """
    works = Works()
    try:
        api_response = works.doi(DOI)
        if api_response:
            return api_response
        return(False)
    except:
        return(False)


def _openurl_direct_information(address):
    """
    input:
        address : Address of the article
        Formate: OpenURL
    output:
        metadata : dictionary containing the metadata of article  
    """
    url_infor = {}
    for pars in parse_qsl(urlparse(address)[4]):
        url_infor[pars[0]] = pars[1]
    return url_infor
