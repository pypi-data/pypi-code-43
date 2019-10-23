import re

import boto3



def validate_email(email_str):
    """
    Basic validation of email:
        Check for '@' symbol.
        Check there are characters before the '@'
        Check there are characters after the '@', including a '.'
    Returns:
        is_valid (bool)
        failed_validation_reason (str)
    """
    if '@' not in email_str:
        return False, "Email is missing @"
    domain = email_str.split("@")[-1]
    pre_domain = email_str.replace(f"@{domain}", "")
    if "." not in domain:
        return False, "Email domain name is missing a '.'"
    if len(pre_domain) == 0:
        return False, "Email appears to be missing the username portion"
    return True, None


def validate_web_host_has_no_scheme(web_host_str):
    """
    Basic validation of 'sub.domain.tld' - make sure http(s):// is not included
    Returns:
        is_valid (bool)
        failed_validation_reason (str)
    """
    if web_host_str.startswith("https://"):
        return False, "Web host includes 'https://' - it should be in the form 'sub.domain.tld'"
    if web_host_str.startswith("http://"):
        return False, "Web host includes 'http://' - it should be in the form 'sub.domain.tld'"
    return True, None


def validate_cert_matches_web_host(cert_arn, web_host):
    """
    Check that the web_host matches the domain the cert is for. Goal is to identify times where the cert will
    definitely not work (i.e. you copy pasted the wrong cert). Pretty stupid, don't rely on a positive response to mean
    that the certificate will work.

    Will fail validation on:
        cert_domain='notexample.com' web_host='dev.example.com'
    Will pass validation on:
        cert_domain='*.example.com' web_host='dev.example.com'
    Will pass validation on, despite cert not working:
        cert_domain='example.com' web_host='dev.example.com'
        cert_domain='example.com' web_host='notexample.com'

    Returns:
        is_valid (bool)
        failed_validation_reason (str)
    """

    acm = boto3.Session().client('acm')

    try:
        resp = acm.describe_certificate(CertificateArn=cert_arn)
    except Exception as ex:
        return True, None  # This doesn't necessarily mean that the cert_arn is invalid, so let it pass validation

    domains = resp["Certificate"]["SubjectAlternativeNames"]

    found_match = False
    for domain in domains:
        if domain.startswith("*"):
            domain = domain[1:]
        if web_host.endswith(domain):
            found_match = True
            break
    if not found_match:
        return False, f"WebHost '{web_host}'' does not appear to be a valid domain for this certificate. The " \
            f"certificate {cert_arn} supports these domains: {domains}"
    else:
        return True, None


VALIDATORS = {}


class UserInputParam:
    def __init__(self, param_name, description, default_value, is_password=False, validation_regex=None, required=True):
        self.name = param_name
        self.description = description
        self.default = default_value
        self.is_password = is_password
        self.validation_regex = validation_regex
        self.required = required
        self._actual = "_NOT_SET"

    def is_valid(self, user_input):
        if self.required:
            if user_input is None:
                return False, f"{self.name} is a required parameter."
            if user_input.strip() == "":
                return False, f"{self.name} is a required parameter."

        if self.validation_regex is not None:
            if re.match(self.validation_regex, user_input) is None:
                return False, f"{self.name} is required to match the regex {self.validation_regex}"

        return True, None

    @property
    def val_is_set(self):
        return self._actual != "_NOT_SET"

    @property
    def param_value(self):
        if not self.val_is_set:
            raise RuntimeError("Trying to retrieve param value that hasn't been set")
        return self._actual

    def set_val(self, val):
        self._actual = val

    def input_prompt(self):
        return f"{self.name}"
