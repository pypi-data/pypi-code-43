# Example: Q9A6F4
# https://www.ebi.ac.uk/proteins/api/doc/#!/proteins/getByAccession

import requests, sys
import xml.etree.ElementTree as ET #parse xml files
from io import StringIO #string to handle
from annofetch.lib.exception.accession_error import AccessionError


def get_root(uniprot_accession):
    requestURL = "https://www.ebi.ac.uk/proteins/api/proteins/"
    requestURL = requestURL + uniprot_accession
    try:
        response = requests.get(requestURL, headers={ "Accept" : "application/xml"})
    except Exception as ex:
        raise AccessionError("Failed to connect to UniProtKB: " +
        type(ex).__name__)
    if not response.ok:
        raise AccessionError("No uniprot-entry for given accession. HTTPError " +
            str(response.status_code))

    """ Parse the response to a handle to a xml-tree file respresented by a root. """
    try:
        responseBody = response.text
        handle = StringIO(responseBody)
        root = ET.parse(handle).getroot()
    except Exception as ex:
        raise AccessionError("No valid uniprot-entry for given accesion: " +
        type(ex).__name__)
    else:
        return root

""" The namespace of the xml file from uniprot.org"""
ns = {'up': 'http://uniprot.org/uniprot'}

### Possible information ###
def get_dbReference(root):
    return root.findall('up:dbReference', ns)

#TODO more than one
def get_accession(root, id):
    list = []
    for ref in root.findall('up:dbReference', ns):
        if ref.get('type') == "EMBL":
            for prop in ref.findall('up:property', ns):
                if prop.get('type') == "protein sequence ID":
                    id = prop.get('value')
                    list.append(id)
    return list

def gene_name(root):
    gene_name = root.find('up:gene/up:name', ns)
    return gene_name.text

#TODO extract dbReference once
""" Get database references for KEGG or EC."""

def get_dbReference(root, db):
    id = ""
    for ref in root.findall('up:dbReference', ns):
        if ref.get('type') == db:
            id = ref.get('id')
            break
    return id

def get_ec(root):
    return get_dbReference(root, "EC")

def kegg_acc(root):
    return get_dbReference(root, "KEGG")

def eggnog_or_cog(root, start): #possible starts: 'COG' or 'ENOG'
    list = []
    for ref in root.findall('up:dbReference', ns):
        if ref.get('type') == "eggNOG":
            id = ref.get('id')
            if id.startswith(start):
                list.append(id)
    return list

def get_pfams(root):
    pfams = []
    for ref in root.findall('up:dbReference', ns):
        if ref.get('type') == "Pfam":
            for prop in ref.findall('up:property', ns):
                if prop.get('type') == "entry name":
                    pfams.append(prop.get('value'))
            break
    return pfams

### UniProt Part ###
def uniprot_part(mydict, root=''):

    """ Get the UniProt accesion """
    acc_list = mydict["UniProt Accession"]
    if len(acc_list) == 0 or acc_list[0] == "":
        return mydict
    uniprot_accession = acc_list[0]

    ### UniProt ###
    """ Reqeust for the xml file if no root is given.
    AccessionError possible. """
    if root == '':
        root = get_root(uniprot_accession)

    if "EC number" in mydict:
        mydict["EC number"] = get_ec(root)

    if "KeggID" in mydict:
        mydict["KeggID"] = kegg_acc(root)

    if "EggNOG" in mydict:
        mydict["EggNOG"] = eggnog_or_cog(root, 'ENOG')

    if "COGID" in mydict:
        cog = eggnog_or_cog(root, 'COG')
        mydict["COGID"] = cog

    if "Gene_name" in mydict:
        name = gene_name(root)
        mydict["Gene_name"] = name

    if "Pfam" in mydict:
        pfams = get_pfams(root)
        mydict["Pfam"] = pfams

    return mydict


### TODO Test ###
def test():# Parse xml file
    root = ET.parse('Files/aak24111.xml').getroot()

def test2():
    get_root("P37059")
