import datetime
import logging
import textwrap

import colorama as ca

from impetuous.cli import get_terminal_width, maybe_elide, one_line
from impetuous.config import CONFIG_DIR, CONFIG_INI_PATH, CodedValue
from impetuous.ext import SubmissionStatus
from impetuous.sheet import Entry, ValidationError, localtz, utcnow

logger = logging.getLogger(__name__)


class Display(object):
    """ Mostly stuff about displaying to the CLI...

    Caches some things, so should be fairly shortish-lived.

    TODO most of the things in here like "print" should be format functions
    that return strings please. This is more useful and simplifies i18n.
    """

    def __init__(self, impetuous):
        self.im = impetuous
        self.local_today = utcnow().astimezone(localtz).date()
        self._terminal_width = None

    @property
    def terminal_width(self):
        if self._terminal_width is None:
            self._terminal_width = get_terminal_width() or 78
        return self._terminal_width

    def _format_validation_err(self, err):
        params = err.params.copy()
        for key, value in params.items():
            if isinstance(value, Entry):
                entry = value
                params[key] = self.at_format(entry)
        return ValidationError(message=err.message, params=params)

    def at_format(self, entry):
        """ foo@420o'clock ...
        """
        return "".join((ca.Style.BRIGHT, entry.text, ca.Fore.BLUE, '@', self.format_datetime(entry.start), ca.Style.RESET_ALL))

    def show(self, entries, *, verbose=False, reverse=False):
        entries = sorted(entries, key=lambda entry: entry.start, reverse=reverse)
        while entries:
            entry = entries.pop(0)
            self.print_entry(entry, verbose=verbose)
            if entries:
                next_entry = entries[0]
                if reverse:
                    gap = entry.start - (next_entry.end or utcnow())
                else:
                    gap = next_entry.start - (entry.end or utcnow())
                if gap > datetime.timedelta(seconds=1):
                    print(ca.Fore.MAGENTA, '(', self.format_timedelta(gap), ')', ca.Style.RESET_ALL, sep='')

    def print_entry_submissions(self, entry, verbose=False):
        config = self.im.get_config_or_none()
        if config is not None:
            for ext, entry, submission in self.im.get_entry_submissions(entry):
                print(' ', end='')
                self.print_entry_submission(ext, entry, submission, verbose=verbose)

    def print_entry_submission(self, ext, entry, submission, *, verbose):
        if (ext.name, submission.key) in entry.submissions:
            status = SubmissionStatus.submitted
        else:
            status = submission.status(entry)
        if verbose:
            print(ext.name, end='')
            print('[', end='')
        else:
            print(ext.abbr, end='')
        if status is SubmissionStatus.invalid:
            print(ca.Style.BRIGHT, ca.Fore.RED, '!', ca.Style.RESET_ALL, sep='', end='')
        elif status is SubmissionStatus.unsubmitted:
            print(ca.Style.BRIGHT, '*', ca.Style.RESET_ALL, sep='', end='')
        if verbose:
            print(submission.label, end=']')

    def print_entry(self, entry, verbose=True):
        #if verbose:
        #    self.print_entry_id(entry, end=' ')
        self.print_entry_start(entry, end=' ')
        self.print_entry_duration(entry, end=' ')
        self.print_entry_end(entry, end=' ')
        self.print_entry_text(entry, end='')
        self.print_entry_submissions(entry, verbose=verbose)
        if verbose:
            print()
            if entry.comment:
                print(textwrap.indent(entry.comment, '  '))
        else:
            if entry.comment: # TODO what in the fuck is going on here?
                room = self.terminal_width - 28 - len(entry.text)  # start
                if entry.start is not None and entry.start.astimezone(localtz).date() != self.local_today:
                    room -= 11
                if entry.end is not None and entry.end.astimezone(localtz).date() != self.local_today:
                    room -= 11
                room -= 2 + 4 # surrounding braces and room for submissions?
                if room > 1:
                    # So, if we have three characters of comment, you just get "(...)"
                    # Which could indicate to the user that there is a comment on that
                    # entry. So that's useful.
                    # There's no point if room is not positive; showing "()" is
                    # confusing.
                    # And if we only have one character of room, you get a boober "(.)"
                    # so the minimum is two characters of room.
                    comment = maybe_elide(one_line(entry.comment), room)
                    print(' (%s)' % comment, end='')
            print()

    def print_entry_id(self, entry, **kwargs):
        print(entry.id, **kwargs)

    def print_entry_text(self, entry, **kwargs):
        print(self.format_entry_text(entry), sep='', **kwargs)

    def print_entry_start(self, entry, **kwargs):
        print(self.format_entry_start(entry), sep='', **kwargs)

    def print_entry_end(self, entry, **kwargs):
        print(self.format_entry_end(entry), sep='', **kwargs)

    def format_entry_text(self, entry, **kwargs):
        return "".join((ca.Style.BRIGHT, entry.text, ca.Style.RESET_ALL))

    def format_entry_start(self, entry, **kwargs):
        return "".join((ca.Style.BRIGHT, self.format_datetime(entry.start)))

    def format_entry_end(self, entry, **kwargs):
        return self.format_datetime(entry.end)

    def format_datetime(self, dt):
        return "".join((ca.Fore.GREEN, self.format_datetime_plain(dt), ca.Fore.RESET))

    def format_datetime_plain(self, dt):
        if dt is None:
            return '--:--:--'
        else:
            dt = dt.astimezone(localtz)
            is_today = dt.date() == self.local_today
            if is_today:
                return dt.time().strftime('%H:%M:%S')
            else:
                return dt.strftime('%Y-%m-%d %H:%M:%S')

    def print_entry_duration(self, entry, **kwargs):
        print(self.format_duration(entry.duration), **kwargs)

    def format_duration(self, delta, **kwargs):
        """ Some colours around format_timedelta()
        """
        return ''.join((ca.Fore.BLUE, ca.Style.BRIGHT, self.format_timedelta(delta), ca.Style.RESET_ALL))

    def format_timedelta(self, delta):
        seconds = int(delta.total_seconds())
        if seconds < 0:
            negate = True
            seconds = abs(seconds)
        else:
            negate = False
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return '{}{:}:{:02}:{:02}'.format('-' if negate else '', hours, minutes, seconds)
