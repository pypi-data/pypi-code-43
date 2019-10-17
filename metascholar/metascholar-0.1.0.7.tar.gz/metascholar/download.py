from crossref.restful import Works
import time
import multiprocessing.dummy as mp 
import requests
import os

def _download_content(DOI, location= None):
    """
    input:
        DOI : DOI of the article
        location : location where the article needs to be stored
    output:
        True: if the article was downloaded succesfully
        False: if the article could not be downloaded succesfully
    Feature:
        Download the Article present in the DOI
    """
    if location == None:
        location = os.getcwd() + "/data_files/"
    flag = 0
    works = Works()
    try:
        api_response = works.doi(DOI)
        if api_response:
            link = api_response.get('link')
            if link:
                for l in link:
                    address = l.get('URL')
                    if 'xml' in address:
                        time.sleep(1)
                        response = requests.get(address)
                        file = DOI.replace("/","")
                        file_name =  location + file +'.xml'
                        if '</html>' not in str(response.content):
                            with open(file_name, 'wb') as f:
                                f.write(response.content)
                            flag = 1
                            return True
                    else:
                        response = requests.get(address)
                        file = DOI.replace("/","_")
                        file_name = location + file +'.pdf'
                        if '</html>' not in str(response.content):
                            with open(file_name, 'wb') as f:
                                f.write(response.content)
                            flag = 1
        if flag == 0:
            return False
        else:
            return True                        
    except:
        return False


def download(DOI, location):
    """
    input:
        DOI : DOI of the article
        location : location where the article needs to be stored
    output:
        True: if the article was downloaded succesfully
        False: if the article could not be downloaded succesfully
    """
    if location[-1] != "/":
        location = location + "/"
    return _download_content(DOI, location)
    

def download_bulk(DOI_list):
    """
    input:
        DOI_list : list of DOIs of the articles
    output:
        List of values of
        True: if the article was downloaded succesfully
        False: if the article could not be downloaded succesfully
    """
    p=mp.Pool(8)
    result = p.map(_download_content, DOI_list) 
    p.close()
    p.join()
    return result

