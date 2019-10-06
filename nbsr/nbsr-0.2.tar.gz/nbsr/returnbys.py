"""Constants that indicate the reason of return of a reading method.

These enum values indicate the reason why the last reading method returned,
i.e.

- EOF
- SIZE
- NEWLINE
- PATTERN
- TIMEOUT

Such constants can be used as attributes of the package, e.g.
``nbsr.returnby_EOF``, ``nbsr.returnby_SIZE``, etc.

See :func:`return_reason()` for details.
"""

returnby_EOF = 0
returnby_NEWLINE = 11
returnby_SIZE = 12
returnby_PATTERN = 20
returnby_TIMEOUT = 100
