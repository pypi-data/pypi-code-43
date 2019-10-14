import re
from datetime import datetime

from PyInquirer import Validator, ValidationError


def non_empty(document) -> None:
    if not document.text:
        raise ValidationError(
            message="Please enter a non-empty value.",
            cursor_position=len(document.text),
        )


def valid_date(document) -> None:
    try:
        datetime.strptime(document.text, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            message="Please enter a valid yyyy-mm-dd date.",
            cursor_position=len(document.text),
        )


email_regex = r"^(\w|\d|\.|\_|\-)+$"


def valid_email_prefix(document) -> None:
    try:
        assert re.match(email_regex, document.text)
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid email prefix (e.g. james.f).",
            cursor_position=len(document.text),
        )


def valid_email_prefix_list(document) -> None:
    try:
        for prefix in document.text.split(","):
            assert re.match(email_regex, prefix.strip())
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid email prefix (e.g. james.f).",
            cursor_position=len(document.text),
        )


def valid_cron(document) -> None:
    cron_regex = r"^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$"
    try:
        if document.text.strip() != "null":
            assert re.match(cron_regex, document.text.strip())
    except AssertionError:
        raise ValidationError(
            message="Please enter a valid cron or null.",
            cursor_position=len(document.text),
        )


class ValidNonEmpty(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a non-empty value."""
        non_empty(document)


class ValidEmailPrefix(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a valid email prefix."""
        non_empty(document)
        valid_email_prefix(document)


class ValidEmailPrefixList(Validator):
    def validate(self, document) -> None:
        non_empty(document)
        valid_email_prefix_list(document)


class ValidClientIds(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid client id list."""
        non_empty(document)


class ValidDate(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a valid yyyy-mm-dd date."""
        non_empty(document)
        valid_date(document)


class ValidOptionalUrl(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid url."""
        non_empty(document)


class ValidUrl(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid url."""
        pass


class ValidUrlList(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid url list."""
        non_empty(document)


class ValidOptionalUrlList(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid url list."""
        pass


class ValidCron(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid crontab style string."""
        non_empty(document)
        valid_cron(document)


class ValidDirectory(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid unix path."""
        non_empty(document)
