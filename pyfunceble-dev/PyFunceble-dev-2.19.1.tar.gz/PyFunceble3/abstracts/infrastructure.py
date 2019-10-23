import PyFunceble3.exceptions as exceptions


class Infrastructure:
    DEFAULT_CONFIGURATION_FILENAME = ".PyFunceble_production.yaml"
    CONFIGURATION_FILENAME = ".PyFunceble.yaml"
    ENV_FILENAME = ".pyfunceble-env"


class Messages:
    # pylint: disable=line-too-long
    INSTALL_CONFIG = {
        "en": "%(not_found_path)s was not found.\nInstall and load the default configuration at the mentioned location? [yes/no] "
    }

    YES_VALUES = ["y"]
    NO_VALUES = ["n"]

    @classmethod
    def get(cls, alias, language):
        """
        Given an alias and a language, we return the message.
        """

        alias = alias.upper()
        language = language.lower()

        if hasattr(cls, alias):
            message = getattr(cls, alias)

            if language in message:
                return message[language]

            raise exceptions.MessageNotFound(
                f"<alias> ({alias}) has nothing for the given language ({language})"
            )
        raise exceptions.MessageNotFound(f"<alias> ({alias}) was not found.)")
