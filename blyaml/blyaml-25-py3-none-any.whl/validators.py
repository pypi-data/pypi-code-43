import re
from datetime import datetime

from PyInquirer import Validator, ValidationError
from prompt_toolkit.document import Document

# This file contains functions used for validation and Validator classes that use them.
# Validators are used by questions.


def non_empty(document: Document) -> bool:
    if not document.text:
        raise ValidationError(
            message="Please enter a non-empty value.",
            cursor_position=len(document.text),
        )
    return True


def valid_date(document: Document) -> bool:
    try:
        datetime.strptime(document.text, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValidationError(
            message="Please enter a valid yyyy-mm-dd date.",
            cursor_position=len(document.text),
        )


email_regex = r"^(\w|\d|\.|\_|\-)+$"


def valid_email_prefix(document: Document) -> bool:
    try:
        assert re.match(email_regex, document.text)
        return True
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid email prefix (e.g. james.f).",
            cursor_position=len(document.text),
        )


def valid_email_prefix_list(document: Document) -> bool:
    try:
        for prefix in document.text.split(","):
            assert re.match(email_regex, prefix.strip())
        return True
    except AssertionError:
        raise ValidationError(
            message="Please enter a comma seperated list of valid email prefixes (e.g. james.f).",
            cursor_position=len(document.text),
        )


url_regex = (
    r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
)


def valid_url(document: Document) -> bool:
    try:
        assert re.match(url_regex, document.text.strip())
        return True
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid url.", cursor_position=len(document.text)
        )


def valid_url_list(document: Document) -> bool:
    try:
        for url in document.text.split(","):
            assert re.match(url_regex, url.strip())
        return True
    except AssertionError:
        raise ValidationError(
            message="Please enter a comma seperated list of valid urls.",
            cursor_position=len(document.text),
        )


def valid_cron(document: Document) -> bool:
    # Cron supports lots of advanced features such as ranges, so the regex is very long.
    cron_regex = r"^(\*|([0-9]|0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|0[0-9]|1[0-9]|2[0-3])|\*\/([0-9]|0[0-9]|1[0-9]|2[0-3])) (\*|([1-9]|0[0-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|0[0-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|0[0-9]|1[0-2])|\*\/([1-9]|0[0-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$"
    try:
        if document.text.strip() != "null":
            assert re.match(cron_regex, document.text.strip())
        return True
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid cron or null.",
            cursor_position=len(document.text),
        )


def valid_directory(document: Document) -> bool:
    directory_regex = r"^(/)?([^/\0]+(/)?)+$"
    try:
        assert re.match(directory_regex, document.text.strip())
        return True
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid unix directory.",
            cursor_position=len(document.text),
        )


class ValidNonEmpty(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a non-empty value."""
        return non_empty(document)


class ValidEmailPrefix(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a valid email prefix."""
        return non_empty(document) and valid_email_prefix(document)


class ValidEmailPrefixList(Validator):
    def validate(self, document: Document) -> bool:
        return non_empty(document) and valid_email_prefix_list(document)


class ValidClientIds(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid client id list."""
        # Checkboxes don't support validation yet.
        # https://github.com/CITGuru/PyInquirer/issues/46
        return True


class ValidDate(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a valid yyyy-mm-dd date."""
        return non_empty(document) and valid_date(document)


class ValidOptionalUrl(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid url."""
        return document.text == "" or valid_url(document)


class ValidUrl(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid url."""
        return non_empty(document) and valid_url(document)


class ValidUrlList(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid url list."""
        return non_empty(document) and valid_url_list(document)


class ValidOptionalUrlList(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid url list."""
        return document.text == "" or valid_url_list(document)


class ValidCron(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid crontab style string."""
        return non_empty(document) and valid_cron(document)


class ValidDirectory(Validator):
    def validate(self, document: Document) -> bool:
        """Return True with no errors for a syntaxtically valid unix path."""
        return non_empty(document) and valid_directory(document)
