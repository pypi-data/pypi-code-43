import argparse
import csv, sys
import annofetch.lib.type as type
from annofetch.lib.exception.config_error import ConfigError

### Argparse input ###
def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="the input file with accesion")
    parser.add_argument("-o", help="name of the output file", dest="output", default="output")
    parser.add_argument("--no-header", help="interpret the first entry as an accession, otherwise the first line is treated as a header and ignored", dest="header", action="store_false")

    #TODO group the flags for accessions exclusively
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--genbank", "--embl", "--ddbj", "--accession", help="flag for the accession embl, ncbi and ddbj use", action="store_true", dest="accession")
    group.add_argument("--gi", help="flag telling that the input contains gi-numbers", action="store_true")
    group.add_argument("--hgnc", help="flag telling that the input contians hgnc accession numbers", action="store_true")
    group.add_argument("--uniprot", help="flag telling that the input contains uniprot accession numbers", action="store_true")

    #optional columns
    parser.add_argument('--cog-category', help="column with the functional category by COG", action="store_true", dest="cog")
    parser.add_argument("--cog-description", help="adds to every functional COG category the description", action="store_true")
    parser.add_argument("--ec", "--ec-number", help="column with ec-numbers", action="store_true")
    parser.add_argument("--eggnog", help="column with eggNOG annotation", action="store_true")
    parser.add_argument("--gene-name", help="the name of the gene of the protein", action="store_true")
    parser.add_argument("--goa", help="column with go annotations", action="store_true", dest='goa')
    parser.add_argument("--kegg", help="column with KEGG annotation", action="store_true")
    parser.add_argument("--no-description", "--no-descr", help="no column with description", action="store_false", dest='description')
    parser.add_argument("--organism", help="column with organism seperated from description", action="store_true")
    parser.add_argument("--pfam", help="column with all Pfams the protein has", action="store_true")
    parser.add_argument("--seq", "--sequence", help="sequence is given", action="store_true")

    args = parser.parse_args()
    return args

""" A dictionary containing all the different confirmation questions. """
confirm = {
type.none: "The given identifiers couldn't be related to valid accessions. \n" +
"Please check the allowed identifiers.",
type.gi: "Are your identifiers gi-numbers (NCBI)? \n" +
"Press y/n and enter to continue: ",
type.accession: "Are your identifiers Accession numbers (GenBank/Ena/DDBJ)? \n" +
"Press y/n and enter to continue: ",
type.uniprot: "Are your identifiers protein accessions from UniProtKB? \n" +
"Press y/n and enter to continue: ",
type.hgnc_or_gi: "The identifier type is not clear. They could match gi-numbers (NCBI)" +
" or HGNC accession numbers. \n" +
"Press 'g' for gi-number or 'h' for HGNC or 'n' if both options don't match.:"
}


""" Read input file """
"""
The given input file should contain only one accession every line and
nothing else. The file is read in line by line taking the content of line
as an accession and storing it in a list.
"""
def read_input(filename):
    accs = []

    try:
        f = open(filename, "r")
    except FileNotFoundError:
        print("Could not find the file:", filename)
        sys.exit()
    except IOError:
        print("Could not read file:", filename)
        sys.exit()
    else:
        accs = (line.strip() for line in f)
        accs = list(line for line in accs if line) #Non-blank lines
        f.close()

    return accs

"""
To confirm the accession and start a protocol the matched and probably
identified accession needs to be confirmed.
This is either be done by a set flag or by a confirmation request.
"""
def confirm_accession(given_type, flag):

    """ When the input did not match any accession type there is no point
    in starting any of the protocols """
    if given_type == type.none:
        return given_type

    """ When the identified type and the flag match, there is no need for
    confirmation and the specific protocol can be selected. """
    if given_type == flag:
        return given_type

    """ When the type hgnc_or_gi is given and the flag is
    either gi or hgnc it also clears which accession to chose. """
    if given_type == type.hgnc_or_gi:
        if flag == type.hgnc:
            return type.hgnc
        elif flag == type.gi:
            return type.gi

    """ When no flag was specified the user has to confirm that the identification
    of the accession was right. """
    if flag == type.none :
        print("***There was no accession flag given.***")
        return user_confirm(given_type)

    """ The default way, which means that flag and the given type do not
    match, is to ask the user weather the given type (not the flag) might be
    right. """
    print("Your accession flag didn't match with the given accessions." )
    #TODO inform the user
    return user_confirm(given_type)

### Dialogs ###
def user_confirm(given_type):
    print(confirm[given_type])
    key = input()
    key.strip().lower

    """ Typing a 'y' for yes confirms the assumed type except when it is
    unsure weather the identifier refers to hgnc or a gi-number """
    if key == 'y' and (given_type != type.hgnc_or_gi):
        return given_type

    """ Typing 'n' means that the assumed identifier is not correct.
    This leads to the abort of the program as the identifier is unknown. """
    if key == 'n':
        return type.none

    """ Only when the identifier could either match a gi-number or hgnc
    'g' is a valid key input. """
    if key == 'g' and given_type == type.hgnc_or_gi:
        return type.gi

    """ Same as for the key 'g' """
    if key == 'h' and given_type == type.hgnc_or_gi:
        return type.hgnc
    else:
        """ If the input matches none of the keys, the request is repeated. """
        print("*** You didn't enter a valid key. Please try it again. ***")
        return user_confirm(given_type)

def email_dialog(config):
    while True:
        key = input("Please enter a valid email address or type exit to quit " +
        "this dialog: ")
        key.strip()

        if key == 'exit':
            sys.exit()

        try:
            if config.set_email(key):
                print("Your email address has been set successfully.")
                break
            else:
                print("***No valid email address. Try again.***")
        except ConfigError as err:
            print(err.message)
            print("As there is a problem within the config file the program " +
            "without an email address.")
            break






### Output ###
def output_file(dicts, output):
    filename = output
    #Add the .csv ending
    if not filename.endswith('.csv'):
        filename = filename + '.csv'
    with open(filename,'w+') as file: #'w+' to create a new file if not existing
        w = csv.DictWriter(file, dicts[0].keys())
        w.writeheader()
        w.writerows(dicts)
        file.close()
    return filename

def append_output(dicts, filename):
    with open(filename,'a+') as file: #'a+' to append the lines
        w = csv.DictWriter(file, dicts[0].keys())
        w.writerows(dicts)
        file.close()
