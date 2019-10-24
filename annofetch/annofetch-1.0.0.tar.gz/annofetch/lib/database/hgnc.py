import requests, sys
from annofetch.lib.exception.accession_error import AccessionError

def getHGNC(hgnc_id):
    requestBody = "http://rest.genenames.org/fetch/hgnc_id/"
    requestURL = requestBody + hgnc_id

    #Get information
    try:
        response = requests.get(requestURL, headers={ "Accept" : "application/json"})
    except Exception as ex:
        raise AccessionError("Failed to connect to HGNC: " +
        type(ex).__name__)

    if not response.ok:
        raise AccessionError("No hgnc-entry for given accession. HTTPError " +
            str(response.status_code))

    """ Parse the response to a json file. """
    try:
        json = response.json()
    except Exception as ex:
        raise AccessionError("No valid hgnc-entry for given accession: " +
        type(ex).__name__)
    else:
        return json

def get_uniprot_acc(result):
    if "uniprot_ids" in result:
        return result["uniprot_ids"]

def get_accession(result):
    if "ena" in result:
        return result["ena"]

def hgnc_part(mydict):
    id = mydict["HGNC Identifier"][0]
    json = getHGNC(id)
    docs = json["response"]["docs"]
    if docs == []:
        raise AccessionError("No hgnc-entry found for given identifier.")

    result = docs[0]
    """ Try to get ena-accession or at least a uniprot accession. """
    accession = get_accession(result)
    if accession:
        if len(accession) > 1:
            mydict["Notification"].append("More than one accession. Picked first.")
        mydict["Accession"] = accession

    uniprot = get_uniprot_acc(result)
    if uniprot:
        if len(uniprot) > 1:
            mydict["Notification"].append("More than one UniProtKB accession. Picked first.")
        mydict["UniProt Accession"] = uniprot
