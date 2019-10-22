'''
( * 
    The following uses EBNF, See the spec here for details.
    https://en.wikipedia.org/wiki/Extended_Backus–Naur_form
* )


space           = " " ;

(* word_breaks are a few words that lets us know the next token should be treated as different. *)
word_breaks     = "and" | "or" ;
words           = { ? Any leftover text that cannot be interpreted as another token. Usually words or characters. ? } ;

digit           = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
time_suffix     = "am" | "pm" ;
date_suffix     = "st" | "nd" | "rd" | "th" ;
delta_prefix    = "in" ;
delta_suffix    = "ago" ;
days            = "monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday" | "sunday" ;
months          = "january" | "february" | "march" | "april" | "may" | "june" | "july" | "august" | "september" | "october" | "november" | "december" ;
relative        = "today" | "tomorrow" | "yesterday" ;
rel_prefix      = "next" | "last" | "this" ;
rel_dur         = ( "second" | "sec" ) | ( "minute" | "min" ) | "hour" | "day" | "week" | "fortnight" | "year" ;
rel_dur_short   = "s" | "m" | "h" ;

time            = { digit } [ ":" { digit } ] [ "." { digit } ] [ time_suffix ] ;
date            = { digit } date_suffix ;

timedelta       = [ delta_prefix ] ( { digit } space rel_dur | { digit } rel_dur_short ) [ { words } timedelta ] [ delta_suffix ] ;
datetime        =
                (
                      { digit } date_suffix 
                    | delta_prefix space timedelta
                    | timedelta space delta_suffix
                    | [ rel_prefix space ] days
                    | months
                    | relative
                ) [ { words } { datetime } ] ;

( *
    Words in between valid datetime / timedelta tokens are stripped,
    otherwise the words are preserved.
* )
'''


import enum
import calendar


class Language(enum.IntFlag):

    EOF = enum.auto()
    WORD = enum.auto()
    DIGIT = enum.auto()

    SECOND = enum.auto()
    MINUTE = enum.auto()
    HOUR = enum.auto()

    DAY = enum.auto()
    WEEK = enum.auto()
    MONTH = enum.auto()
    YEAR = enum.auto()

    SECONDS = enum.auto()
    MINUTES = enum.auto()
    HOURS = enum.auto()
    DAYS = enum.auto()
    WEEKS = enum.auto()
    MONTHS = enum.auto()
    YEARS = enum.auto()

    PREFIX = enum.auto()
    SUFFIX = enum.auto()

    DURATION = enum.auto()
    DATE = enum.auto()
    TIME = enum.auto()

    RELATIVE = enum.auto()
    BREAKPOINT = enum.auto()

    DATETIME = TIME | DATE | YEAR | MONTH | DAY | WEEK | HOUR | SECOND | MINUTE
    TIMEDELTA = DURATION | SECONDS | HOURS | MINUTES | DAYS | WEEKS | MONTHS | YEARS


LANGMAP = {
    Language.DAY: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
    Language.MONTH: [m.lower() for m in calendar.month_name[1:]],
    Language.RELATIVE|Language.DATE: ['today', 'tomorrow', 'overmorrow', 'yesterday'],
    Language.RELATIVE|Language.DATE|Language.PREFIX: ['next', 'last', 'this'],
    Language.RELATIVE|Language.DURATION|Language.SUFFIX: ['ago'],
    Language.RELATIVE|Language.DURATION|Language.PREFIX: ['in'],
    Language.DURATION|Language.SUFFIX: 
    [
        # I decided to be extremely specific about which ones support the s
        # suffix so this is manually specified here.

        'second', 'seconds', 'sec', 's', 'minute', 'minutes', 'min', 'm',
        'hour', 'hours', 'hr', 'h', 'day', 'days',
        'week', 'weeks', 'fortnight', 'fortnights', 'month', 'months',
        'year', 'years',
    ],
    Language.WORD|Language.BREAKPOINT: ['and', 'or'],
    Language.DATE|Language.SUFFIX: ['st', 'nd', 'rd', 'th'],
    Language.TIME|Language.SUFFIX: ['am', 'pm'],
    Language.DATE|Language.TIME: ['now'],
}

