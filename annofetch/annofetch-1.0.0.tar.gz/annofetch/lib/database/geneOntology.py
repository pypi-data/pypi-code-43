# Example: Q9A6F4
# https://www.ebi.ac.uk/QuickGO/api/index.html#!/annotations/annotationLookupUsingGET
import requests, sys
from annofetch.lib.exception.accession_error import AccessionError

def getGOA(gene_product_id):
    requestBody = "https://www.ebi.ac.uk/QuickGO/services/annotation/search?geneProductId="
    requestURL = requestBody + gene_product_id

    """ Get a json file for the uniprot accession. """
    try:
        response = requests.get(requestURL, headers={ "Accept" : "application/json"})
    except Exception as ex:
        raise AccessionError("Failed to connect to QuickGO: " +
        type(ex).__name__)

    if not response.ok:
        raise AccessionError("No GO Annotations for the uniprot accession: " +
            str(response.status_code))

    """ Parse the response to a handle to a json file. """
    try:
        responseBody = response.json()
    except Exception as ex:
        raise AccessionError("No valid GO Annotations for the uniprot accession: " +
            type(ex).__name__)
    else:
        return responseBody


def go_ids(json):
    list = []
    go_id = ""
    for result in json["results"]:
        go_id = result["goId"]
        list.append(go_id)
    return list

def geneOntology_part(mydict):
    acc_list = mydict["UniProt Accession"]
    if not "GO Annotation" in mydict or len(acc_list) == 0 or acc_list[0] == "":
        return mydict

    acc = acc_list[0]
    json = getGOA(acc)
    mydict["GO Annotation"] = go_ids(json)

    return mydict
