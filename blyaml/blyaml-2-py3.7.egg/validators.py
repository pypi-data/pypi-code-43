import re

from PyInquirer import Validator, ValidationError


class ValidEmailPrefix(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a valid email prefix."""
        pass


class ValidEmailPrefixList(Validator):
    def validate(self, document) -> None:
        pass


class ValidClientIds(Validator):
    def validate(self, document) -> None:
        pass


class ValidDate(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a valid yyyy-mm-dd date."""
        pass


class ValidUrl(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid url."""
        pass


class ValidUrlList(Validator):
    def validate(self, document) -> None:
        pass


class ValidCron(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid crontab style string."""
        pass


class ValidDirectory(Validator):
    def validate(self, document) -> None:
        """Throws no errors for a syntaxtically valid unix path."""
        pass
