from msg91_otp.country_code import CountryCode
from msg91_otp.exceptions import InvalidCountryCode
from msg91_otp.response import ServiceResponse

def prefix_country_code(country_code, number):
    """Prefix country code to phone number
    Args:
        country_code: the country code to prefix of type CountryCode
        number (str): the mobile number
    Raises:
        InvalidCountryCode when supplied country code is not type of CountryCode
    Returns:
        number (str): mobile number with country code prefixed. if country_code
        is already prefixed, then the same is returned unaltered.
    """
    if not isinstance(country_code, CountryCode):
        raise InvalidCountryCode("The country code should be of type CountryCode")
    if len(number) == 10 and (not number.startswith(country_code.value)):
            number = country_code.value + number
    return number

def convert_response(response_obj, **kwargs):
    """Convert requests package response obj to our internal Response
    Args:
        response_obj: the response object returned by requests package
        kwargs : any other optional keyword parameters
    Returns:
        our internal ServiceResponse object
    """
    if response_obj.json().get('type') == "error":
        message = response_obj.json().get('message')
        status_code = 400
    elif response_obj.json().get('type') == "success":
        message = response_obj.json().get('message')
        status_code = 200
    _response = ServiceResponse(status_code, message, **kwargs)
    return _response
