#Example: 1342363
from Bio import Entrez
from Bio import SeqIO
from urllib.error import HTTPError
from http.client import IncompleteRead
from annofetch.lib.exception.accession_error import AccessionError
from annofetch.lib.exception.config_error import ConfigError
from annofetch.lib.configuration.config import Config

"""
Get infos from NCBI database
9.6  EFetch: Downloading full records from Entrez
http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc68
"""


#TODO
""" Get the corresponding accession or a given gi-number """
def get_accession(gi_number):
    """ Tell the NCBI who is accessing their database """
    Entrez.email = get_email()

    try:
        raw = Entrez.efetch(db="nucleotide", id=gi_number, rettype="acc")
    except HTTPError as err:
        #TODO does that work? -> test
        raise AccessionError(str(err.code) + ": " + err.reason)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args) #TOOD necessary?
        raise AccessionError(message)

    try:
        acc = raw.read()
    except IncompleteRead as err:
        raise AccessionError("No Accession for this gi-number: IncompleteRead Error.")
    except Exception as err:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args) #TOOD necessary?
        raise AccessionError(message)
    else:
        return str(acc).strip()

def get_email():
    config = Config()
    """ Try to get the email. If an error occurs the standard values are set
    anyway. """
    try:
        config.read_config()
    except ConfigError:
        pass

    return config.email
