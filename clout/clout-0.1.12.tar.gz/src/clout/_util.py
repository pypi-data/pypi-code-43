import inflection


UNSET = "__UNSET__"


def dasherize(s: str) -> str:
    return inflection.dasherize(inflection.underscore(s)).lower()
