import PyFunceble3.abstracts as abstracts
import PyFunceble3.shared as shared


def tool():
    """
    Provides the CLI tool.
    """

    if __name__ == "PyFunceble3":
        cli = abstracts.CLIText()
        print(shared.CONFIGURATION)
