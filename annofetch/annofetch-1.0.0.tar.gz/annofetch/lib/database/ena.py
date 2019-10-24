#  Example: AAK24111
# https://www.ebi.ac.uk/ena/browser/api/#/ENA_Browser_Data_API/getFlatFileUsingGET
import requests, sys
from Bio import SeqIO
from io import StringIO
import annofetch.lib.regex as regex
from annofetch.lib.exception.accession_error import AccessionError

def get_ena_record(acc):

    """ Reqeuste URL for ena """
    requestBody = "https://www.ebi.ac.uk/ena/browser/api"
    format = "/embl"
    requestURL = requestBody + format + "/" + acc

    """ Get an embl format for the given accession"""
    try:
        response = requests.get(requestURL, headers={ "Accept" : "text/plain"})
    except Exception as ex:
        raise AccessionError("Failed to connect to EMBL: " +
        type(ex).__name__)

    if not response.ok:
        raise AccessionError("No ena-entry for given accession. HTTPError " +
            str(response.status_code))

    """ Parse the response to a handle to a record. """
    try:
        responseBody = response.text
        handle = StringIO(responseBody)
        record = SeqIO.read(handle, "embl")
    except Exception as ex:
        raise AccessionError("No valid ena-entry for given accession: " +
        type(ex).__name__)
    else:
        return record

""" Possible database refernces to UniProtKB are normally listed in the
feature CDS. As it is possible to have more than one UniProt accession a list
of UniProt accession is generated and checked later on. """
def get_protein_accession(record):
    list = []
    for feature in record.features:
        if feature.type == "CDS":
            qualifiers = feature.qualifiers.get("db_xref")
            for entry in qualifiers:
                if "UniProtKB" in entry or "TrEMBL" in entry or"Swiss-Prot" in entry:
                    uniprot_accession = regex.get_uniprot_accession(entry)
                    if uniprot_accession:
                        list.append(uniprot_accession)
    return list

def get_description(record):
    return record.description

def get_organism(record):
    return record.annotations["organism"]

def get_sequence(record):
    return record.seq


### ENA Part ###
def ena_part(mydict):
    """ Get the accession out of the dict. If there is no accession, skip
    the ena part. """
    acc_list = mydict["Accession"]
    if len(acc_list) == 0 or acc_list[0] == "":
        return mydict
    acc = acc_list[0]

    """ Can raise an AccessionError """
    record = get_ena_record(acc)

    if "Organism" in mydict:
        mydict["Organism"] = get_organism(record)

    if "Description" in mydict:
        description = get_description(record)
        """ Within an description often the organism is included.
        If the organism is also asked, it is cut out of the description. """
        if "Organism" in mydict:
            description = regex.shorten_descr(description, mydict["Organism"])

        mydict["Description"] = description

    if "Sequence" in mydict:
        mydict["Sequence"] = str(get_sequence(record))

    if mydict["UniProt Accession"] == []:
        uniprot_list = get_protein_accession(record)
        if len(uniprot_list) > 1:
            mydict["Notifications"].append("More than one UniProt Accession. Picked first.")

        mydict["UniProt Accession"] = uniprot_list

    return mydict
