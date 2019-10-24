import getopt
import logging
import sys
import traceback
from ResifDataTransfer.DataTransfer import Transfer
from ResifDataTransfer.usage import USAGE


def main():
    try:
        # set default return code
        returncode = 1

        # build usage text
        usage = USAGE.format(
            prog=sys.argv[0],
            appname=Transfer.APPNAME,
            version=str(Transfer.VERSION[0]) + "." + str(Transfer.VERSION[1]),
            config=Transfer.myConfigurationFile,
            contact=Transfer.CONTACT,
            vmin=str(Transfer.PYTHON_VERSION_MIN),
            vmax=str(Transfer.PYTHON_VERSION_MAX),
            bold="\033[1m",
            clear="\033[0m",
        )

        # set some default parameters
        testOnly = False
        ignoreLimits = False
        alternateConfigFile = None
        operationCode = 0
        directory = None
        datatype = None
        transaction = None

        # empty command line ?
        if len(sys.argv[1:]) == 0:
            sys.stderr.write("-h for usage summary.\n")
            sys.exit(2)

        # extract command line arguments
        options, args = getopt.gnu_getopt(
            sys.argv[1:],
            "htc:is:d:r:lv",
            [
                "help",
                "test",
                "config=",
                "ignore-limits",
                "send=",
                "data-type=",
                "retrieve-logs=",
                "logbook",
                "version",
            ],
        )
        for opt, arg in options:
            if opt in ("-h", "--help"):
                print(usage)
                returncode=0
                exit(0)
            elif opt in ("-v", "--version"):
                sys.stderr.write("%d.%d\n" % (Transfer.VERSION))
                returncode=0
                exit(0)
            elif opt in ("-t", "--test"):
                testOnly = True
            elif opt in ("-c", "--config"):
                alternateConfigFile = arg
            elif opt in ("-i", "--ignore-limits"):
                ignoreLimits = True
            elif opt in ("-s", "--send"):
                operationCode += Transfer.OPERATIONS["SEND_DATA"]
                directory = arg
            elif opt in ("-d", "--data-type"):
                datatype = arg
            elif opt in ("-r", "--retrieve-logs"):
                operationCode += Transfer.OPERATIONS["RETRIEVE_LOGS"]
                transaction = arg
            elif opt in ("-l", "--logbook"):
                operationCode += Transfer.OPERATIONS["PRINT_LOGBOOK"]

        # initialize class
        myTransfer = Transfer(
            test=testOnly,
            configurationFile=alternateConfigFile,
            operation=operationCode,
            directoryName=directory,
            dataType=datatype,
            transactionID=transaction,
            ignoreLimits=ignoreLimits,
        )

        # launch operation
        returncode = myTransfer.start()

    # error while parsing command line arguments
    except getopt.GetoptError as err:
        sys.stderr.write(str(err) + ". Use -h to display usage.\n")
        returncode = 2
    # keyboard interrupt
    except KeyboardInterrupt:
        returncode = 1
        logging.error("keyboard interrupt")
    # any other exception
    except Exception as myException:
        returncode = 1
        traceback.print_exc(None, file=sys.stderr)
        logging.error(str(myException))
    # executed anytime
    finally:
        #traceback.print_exc(None, file=sys.stderr)
        return(returncode)


if __name__ == "__main__":
    main()
