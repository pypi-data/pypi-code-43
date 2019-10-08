import re

EMAIL_USER_REGEX = r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z" \
                   '|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)'
EMAIL_USER_REGEX_COMPILED = re.compile(EMAIL_USER_REGEX, re.IGNORECASE)

EMAIL_DOMAIN_REGEX = r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z'
EMAIL_DOMAIN_REGEX_COMPILED = re.compile(EMAIL_DOMAIN_REGEX, re.IGNORECASE)


def valid_email(email):
    if not email or '@' not in email:
        return False

    user_part, domain_part = email.rsplit('@', 1)

    # validate user part
    if not EMAIL_USER_REGEX_COMPILED.match(user_part):
        return False

    # validate domain part
    if not EMAIL_DOMAIN_REGEX_COMPILED.match(domain_part):
        return False

    return True