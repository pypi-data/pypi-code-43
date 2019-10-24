import annofetch.lib.database.ncbi as ncbi
import annofetch.lib.database.uniprot as uniprot
import annofetch.lib.database.geneOntology as GO
import annofetch.lib.database.cog as cog
import annofetch.lib.database.ena as ena
import annofetch.lib.database.hgnc as hgnc

import annofetch.lib.myIO as IO
import annofetch.lib.type as type
import annofetch.lib.regex as regex
import time, re, sys

from annofetch.lib.exception.accession_error import AccessionError

""" According with the given type the protocol is selected """
def select_protocol(given_type):
    if given_type == type.gi:
        return gi_protocol
    elif given_type == type.accession:
        return ena_protocol
    elif given_type == type.uniprot:
        return uniprot_protocol
    elif given_type == type.hgnc:
        return hgnc_protocol
    elif given_type == type.hgnc_or_gi:
        raise AccessionError("I am sorry but for some unknonw reason the " +
        "program was unable to identify your accession type and could not " +
        "select an appropriate protocol.")
    else:
        raise AccessionError("**Programmer too stupid Error***\n" +
        "Something totally went wrong by the selection of a protocol: " +
        given_type)

""" Main Protocol
The main protocol handles the information of every accession in the given
accession list.
Therefore it goes through the list and for each accession starts the given protocol.
All retrieved information is stored within a dict which in turn is stored
in a list.
When reaching the limit of dicts in the list (the limit is specified in the
config.py file) the information is exported to the output file.
"""
def main_protocol(protocol, accs, args, config):
    dicts = [] # list for all dictionaries
    first = True # boolean weather it is the first output time
    filename = ""

    """ Preparation of the COG files.
    In opposite to all the other information the COG functional annotation
    is not searched in a database. But the information is contained in files
    which are read in if the user asked for the COG annotation.
    """
    cognames = {}
    fun = {}
    if args.cog or args.cog_description:
        cognames = cog.get_cognames()
        fun = cog.get_cog_fun()

    """ Go through the list of accessions """
    for id in accs:

        print("Given ID: " + id)

        mydict = {}
        try:
            """ Fill mydict with keys """
            root = protocol(mydict, id, args)
        except AccessionError as err:
            mydict["Notification"].append(err.message)
            print("*** AccessionError ***")
            pass
        else:
            """ Retrieve all information from ena. """
            try:
                mydict = ena.ena_part(mydict)
            except AccessionError as err:
                mydict["Notification"].append(err.message)

            """  Retrieve all information from UniProtKB.
            When the uniprot protocol was executed the uniprot database
            was already requested and the information is stored within root """
            #TODO current workpoint
            try:
                if root:
                    mydict = uniprot.uniprot_part(mydict, root)
                else:
                    mydict = uniprot.uniprot_part(mydict)

                """ Get all GO Terms """
                mydict = GO.geneOntology_part(mydict)
                """ Get all information about COG """
                mydict = cog.cog_part(mydict, cognames, fun)
            except AccessionError as err:
                mydict["Notification"].append(err.message)

        """ Turn all lists within mydict into comma separated strings """
        for key,value in mydict.items():
            if isinstance(value, list):
                mydict[key] = list_to_string(value)

        dicts.append(mydict)

        if len(dicts) == config.lines_to_file:
            if first:
                filename = IO.output_file(dicts, args.output)
                first = False
            else:
                IO.append_output(dicts, filename)
            dicts.clear()

        time.sleep(config.query_pause) #just in case TODO

    #append the last lines
    if len(dicts) > 0:
        if first:
            IO.output_file(dicts, args.output)
        else:
            IO.append_output(dicts, filename)


### Preprataion of dicts ###
""" The Accession for Ena/Genbank/DDBJ as well as the accession for Uniprot
are lists because later on there migth be more than one accession. """
def gi_protocol(mydict, id, args):
    #mydict = {"GI-Number" : id, "Accession" : "", "Uniprot Accession": ""}
    """ There may not raise an error doing this so that the dict is filled
    with (empty) key fields even if the program afterwards fails to extract
    the accession """
    mydict["GI-Number"] = id
    mydict["Accession"] = []
    mydict["UniProt Accession"] = []
    mydict = preprare_dict(mydict, args)

    #gi_id = id[3:] #TODO
    """ Try to extract the gi-number out of the given string"""
    match = regex.get_gi_or_hgnc(id)
    if match:
        mydict["GI-Number"] = match
    else:
        """ For some reason no number which could be a gi-number
        was found. """
        raise AccessionError("No valid gi-number.")

    """ Can also raise an AccessionError when the http request fails """
    acc = ncbi.get_accession(mydict["GI-Number"])
    mydict["Accession"] = [acc]

    #return mydict

def ena_protocol(mydict, id, args):
    #mydict = {"Accession" : id, "UniProt Accession" : ""}
    mydict["Accession"] = id
    mydict["UniProt Accession"] = []
    mydict = preprare_dict(mydict, args)

    """ Try to extract the accession out of the given string"""
    match = regex.get_accession(id)
    if match:
        mydict["Accession"] = [match]
    else:
        """ No valid Accession could be found. """
        raise AccessionError("No valid Accession.")

def uniprot_protocol(mydict, id, args):
    #mydict = {"UniProt Accession" : id, "Accession" : ""}
    mydict["UniProt Accession"] = [id]
    mydict["Accession"] = []
    mydict = preprare_dict(mydict, args)

    """ Try to extract the uniprot accession out of the given string"""
    match = regex.get_uniprot_accession(id)
    if match:
        mydict["UniProt Accession"] = [match]
    else:
        """ For some reason no number which could be a gi-number
        was found. """
        raise AccessionError("No valid UniProt Accession")

    root = uniprot.get_root(mydict["UniProt Accession"][0])
    acc = uniprot.get_accession(root, id)
    if (len(acc) > 1):
        mydict["Notification"].append("More than one Accession. Picked first.")
    mydict["Accession"] = acc

    """ As within the uniprot protocol the UniProt database is already requested
    we pass the result to the uniprot_part to not reqeust the database
    twice """
    return root

def hgnc_protocol(mydict, id, args):
    mydict["HGNC Identifier"] = [id]
    mydict["UniProt Accession"] = []
    mydict["Accession"] = []
    mydict = preprare_dict(mydict, args)

    """ Try to extract the identifier out of the given string"""
    match = regex.get_gi_or_hgnc(id)
    if match:
        mydict["HGNC Identifier"] = [match]
    else:
        """ No valid HGNC Identifier could be found. """
        raise AccessionError("No valid Accession.")

    """ To get through the parts an Accession or at least a UniProt accession
    is necessary. """
    hgnc.hgnc_part(mydict)

    """ Check weather an accession was found. If there is no accession but a
    UniProt acccession do the same as within the uniprot_protocol. """
    if len(mydict["Accession"]) >= 1:
        return
    elif len(mydict["UniProt Accession"]) >= 1:
        root = uniprot.get_root(mydict["UniProt Accession"][0])
        acc = uniprot.get_accession(root, id)
        if (len(acc) > 1):
            mydict["Notification"].append("More than one Accession. Picked first.")
        mydict["Accession"] = acc
        return root
    """ If no further accession was found, nothing is done yet. """



def preprare_dict(mydict, args):
    if args.organism:
        mydict["Organism"] = ""

    if args.description:
        mydict["Description"] = ""

    if args.ec:
        mydict["EC number"] = ""

    if args.goa:
        mydict["GO Annotation"] = []

    if args.eggnog:
        mydict["EggNOG"] = []

    if args.kegg:
        mydict["KeggID"] = []

    if args.gene_name:
        mydict["Gene_name"] = ""

    if args.pfam:
        mydict["Pfam"] = []

    if args.cog or args.cog_description:
        mydict["COGID"] = []
        mydict["COG category"] = []

        if args.cog_description:
            mydict["COG description"] = []

    if args.seq:
        mydict["Sequence"] = ""

    """ One comment column at the end of every dict to store any
    notifications or errors that occur """
    mydict["Notification"] = []

    return mydict

def list_to_string(list):
    return ",".join(list)
