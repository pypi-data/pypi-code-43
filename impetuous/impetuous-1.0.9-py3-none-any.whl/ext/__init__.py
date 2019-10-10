import logging
import re
from abc import ABC, abstractmethod, abstractproperty
from enum import Enum

import attr

from impetuous.config import CodedValue

logger = logging.getLogger(__name__)

SECRET = 'secret'  # Mark configuration values as secrets, for encoding/decoding


class LudicrousConditions(Exception):
    """
    Raise when when the module can't complete a request due invalid state like
    incomplete configuration or the weather or something. The program may
    display your error and quit or ignore it.
    """

    def __init__(self, error, suggestion):
        self.error = error
        self.suggestion = suggestion

    #def unwrap(self):
    #    if isinstance(self.error, Exception):
    #        wrapped = self.error
    #    elif isinstance(self.suggestion, Exception):
    #        wrapped =  self.suggestion
    #    else:
    #        wrapped = None
    #    if hasattr(wrapped, 'unwrap'):
    #        wrapped = wrapped.unwrap()
    #    return wrapped


class ConfigRequired(LudicrousConditions):

    @classmethod
    def from_attrs(cls, exc, other, section):
        setme = ", ".join(f"`{field.name}`" for field in attr.fields(other))
        return cls(exc, f"Maybe edit your config and set, {setme}, under the `[{section}]` section.")



class SubmissionStatus(Enum):

    invalid = 0
    unsubmitted = 1
    submitted = 2


class API(ABC):

    @abstractproperty
    def identifier(self):
        """ A short string to pick this guy out of a crowd ...
        """

    @abstractmethod
    def discover(self, impetuous, *entries):
        """ yield (entry, Submission) pairs.
        """

    @abstractmethod
    async def agent(self, impetuous, ext):
        """
        Produce an object with a submit(Submission) coroutine method that can
        submit submissions to the given `ext`.
        """

    @classmethod
    def from_somewhere(cls, impetuous, section):
        return cls.from_config(impetuous.get_config_or_empty(), section)

    @classmethod
    def coded_fields(cls):
        return [field for field in attr.fields(cls) if field.metadata.get(SECRET)]

    @classmethod
    def from_config(cls, section):
        try:
            return cls(**{
                field.name:
                    CodedValue.decode_from_config(section, field.name)
                    if field.metadata.get(SECRET)
                    else section[field.name]
                for field in attr.fields(cls)
            })
        except KeyError as e:
            raise ConfigRequired.from_attrs('Key missing: %s' % e, cls, section.name)

    def discover_by_pattern(self, entry, pattern):
        logger.debug(_("%s looking for matches in %r using pattern %s."), type(self).__name__, entry.text, pattern)
        for match in re.findall(pattern, entry.text):
            logger.debug(_("%s found %r in %r using pattern %s."), type(self).__name__, match, entry.text, pattern)
            yield match


@attr.s(frozen=True)
class Submission(object):  # TODO this has the same name as impetuous.sheet.Submission
    """ A submission, maybe posted, maybe not, maybe not even postable.
    """
    # String to identify the submission for some extension in the db
    key = attr.ib()
    # Anything your heart desires ...
    data = attr.ib()
    # Short but readable label to identify the submission.
    label = attr.ib(default=attr.Factory(lambda self: self.key, takes_self=True))

    # TODO this should probably be an attribute as well ... almost positively
    # ... like absolutely, right? ... FIXME XXX
    def status(self, entry) -> SubmissionStatus:
        if entry.end is None:
            return SubmissionStatus.invalid
        elif entry.duration.total_seconds() <= 0:
            return SubmissionStatus.invalid
        elif entry.duration.total_seconds() < 60:
            logger.warning(_("%s has fewer than 60 seconds of time logged. JIRA/things will lose their minds I try to log this."), entry.text)
            return SubmissionStatus.invalid
        else:
            return SubmissionStatus.unsubmitted


@attr.s(frozen=True)
class Ext(object):
    """
    Modules allow for talking to external APIs so you can post time to JIRA or
    Freshdesk or whatever.

    #They shouldn't be too slow, as they may be created and run frequently, such
    #as whenever a entry is printed.
    """
    api = attr.ib()
    abbr = attr.ib()
    name = attr.ib()
