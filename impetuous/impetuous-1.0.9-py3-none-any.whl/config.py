import codecs
import collections
import configparser
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
CONFIG_DIR = Path.home() / ".config" / "impetuous"
CONFIG_INI_PATH = CONFIG_DIR / "config.ini"


class CodedValue(object):
    """ Some bytes encoded with codecs in that order.
    """

    def __init__(self, value: bytes, codecs: list):
        self.value = value
        self.codecs = codecs

    def __repr__(self):
        return "CodedValue(value={!r}, codecs={!r})".format(self.value, self.codecs)

    def __eq__(self, other):
        return self.value == other.value and self.codecs == other.codecs

    @property
    def is_encoded(self) -> bool:
        return bool(self.codecs)

    @property
    def encoded(self) -> str:
        """ Returns coded value as string.
        """
        return self.value.decode()  # convert to string

    @property
    def decoded(self) -> str:
        """ Returns decoded value as string.
        """
        if self.codecs:
            return self.decode().decoded
        else:
            return self.value.decode("utf-8")

    @property
    def config_key_suffix(self):
        return ".".join([""] + self.codecs)

    def decode(self):
        *codecs_, codec = self.codecs
        # Some of the binary codecs have characters that can't exist in a utf-8
        # string I guess, so in order to guarantee that a CodedValue can be
        # represented as a string, so that we can use it in a config file, we
        # base64 the output of every encoding (including base64 encoding)!
        return CodedValue(
            codecs.decode(codecs.decode(self.value, "base64"), codec), codecs_
        )

    def encode(self, codec):
        return CodedValue(
            codecs.encode(codecs.encode(self.value, codec), "base64"),
            self.codecs + [codec],
        )

    @classmethod
    def plain(cls, value: str):
        return cls(value.encode(), [])

    @classmethod
    def from_config(cls, section, key):
        keys = [key_ for key_ in section.keys() if key_.startswith(key + ".")]
        if len(keys) > 1:
            raise KeyError(
                "Ambiguous configuration, %r could be any of %r" % (key, keys)
            )
        elif len(keys) == 1:
            key = keys[0]
            _, *codecs = key.split(".")
            return CodedValue(section[key].encode(), codecs)
        else:
            return CodedValue(section[key].encode(), [])

    @classmethod
    def decode_from_config(cls, section, key):
        return cls.from_config(section, key).decoded


class ConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        can_you_not_just_treat_the_password_as_a_raw_string_or_something = None
        super().__init__(
            *args,
            interpolation=can_you_not_just_treat_the_password_as_a_raw_string_or_something,
            **kwargs
        )


def get_config(path=CONFIG_INI_PATH):
    config = ConfigParser()
    with path.open() as fp:
        config.read_file(fp)
    return config


# TODO use a safer write like how sheet files do it
def write_config(config, path=CONFIG_INI_PATH):
    with path.open("w") as fp:
        config.write(fp)


# TODO look at the bottom stuff and throw it out ...

# def fancy_extract_section_api(section):
#    section_apis = []
#
#    # This kind of rearranging and validating is lame but the config file
#    # format ends up looking nice at least?
#    for ident, cls in API_CLASSES.items():
#        api_data = {
#            key[len(ident)+1:]: value
#            for key, value in section.items()
#            if key.startswith(ident + '.')
#        }
#        if api_data:
#            section_apis.append(cls(**api_data))
#
#    if not section_apis:
#        logger.warning(_("No API information found for section `%s'"), section.name)
#    elif len(section_apis) > 1:
#        raise ValueError("Multiple APIs (%s) found for section `%s'; there can be only one!"
#                            % (", ".join(api.identifier for api in section_apis), section.name))
#    else:
#        return section_apis[0]
#
#
# def fancy_get_exts(config):
#    """ Get exts specified in the config
#    """
#    for __, section in config.items():
#        if section.name == 'DEFAULT':
#            continue
#        api = extract_section_api(section)
#        name = section.name
#        assert name, "Unnamed sections are for jerks"
#        yield Ext(api=api, name=name, abbr=section.get('abbr', name[0]),
#                  pattern=section['pattern'])
