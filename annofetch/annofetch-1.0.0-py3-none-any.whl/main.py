import sys
import annofetch.lib.regex as regex
import annofetch.lib.protocols as protocols
import annofetch.lib.myIO as IO
import annofetch.lib.type as type
from annofetch.lib.configuration.config import Config

from annofetch.lib.exception.accession_error import AccessionError
from annofetch.lib.exception.config_error import ConfigError

def main():

    """ Read the terminal input """
    args = IO.parse_input()

    """ Read the config file and check the email. """
    #TODO current workpoint
    config = Config()
    try:
        config.read_config()
    except ConfigError as err:
        print(err.message)
        print("The program rewrites the config file and continues with default values.")
        try:
            config.write_config()
        except ConfigError as err:
            print(err.message)
    else:
        if not config.check_email():
            print("***There is no valid email address given yet.***")
            print("The email address is required to request " +
            "the NCBI database.")
            IO.email_dialog(config)

    """ Read the given file. """
    accs = IO.read_input(args.input)

    """ Identify the right Accession """
    if len(accs) > 0:
        if args.header:
            """ Remove the first accession as it is a header. """
            accs.pop(0)
            """ Check weather there is still at least one accession left """
            if len(accs) == 0:
                print("No accessions given. The file seems to have only a header.")
                sys.exit()
        ref_acc = accs[0]
        given_type = regex.which_accession(ref_acc)
    else:
        print("No accessions given. The file seems to be empty.")
        sys.exit()

    """ Identify a optionally given flag """
    flag = regex.which_flag(args)

    """ Confirm the identified accession type """
    given_type = IO.confirm_accession(given_type, flag)

    """ When the given input ids could not be identified the program aborts."""
    if given_type == type.none: #TODO AccessionError
        print(IO.confirm[given_type])
        sys.exit()

    """ Select the appropriate protocol """
    try:
        protocol = protocols.select_protocol(given_type)
    except AccessionError as err:
        print(err.message)
        sys.exit()

    """ Start the main protocol to retrieve all information. """
    protocols.main_protocol(protocol, accs, args, config)

    ### Write output to file ###
    print("Done.")
