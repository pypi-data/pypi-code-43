import logging

from apistar import App, http
from xmltodict import parse
from apistellar import Controller, get, settings, Session, redirect, coroutinelocal
from flask_cas.cas_urls import create_cas_login_url
from flask_cas.cas_urls import create_cas_logout_url
from flask_cas.cas_urls import create_cas_validate_url


try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

logger = logging.getLogger("cas")


class CasController(Controller):

    @get()
    def login(self, app: App,
              session: Session,
              host: http.Header,
              port: http.Port,
              scheme: http.Scheme,
              ticket: str=None):
        """
        This route has two purposes. First, it is used by the user
        to login. Second, it is used by the CAS to respond with the
        `ticket` after the user logs in successfully.

        When the user accesses this url, they are redirected to the CAS
        to login. If the login was successful, the CAS will respond to this
        route with the ticket in the url. The ticket is then validated.
        If validation was successful the logged in username is saved in
        the user's session under the key `CAS_USERNAME_SESSION_KEY` and
        the user's attributes are saved under the key
        'CAS_USERNAME_ATTRIBUTE_KEY'
        """
        login_url = f"{scheme}://{host}{app.reverse_url('view:cas:login')}"
        cas_token_session_key = settings['CAS_TOKEN_SESSION_KEY']

        redirect_url = create_cas_login_url(
            settings['CAS_SERVER'],
            settings['CAS_LOGIN_ROUTE'],
            login_url)

        if ticket:
            session[cas_token_session_key] = ticket

            if validate(ticket, login_url, session):
                if 'CAS_AFTER_LOGIN_SESSION_URL' in session:
                    redirect_url = session.pop('CAS_AFTER_LOGIN_SESSION_URL')
                else:
                    redirect_url = app.reverse_url(settings['CAS_AFTER_LOGIN'])
            else:
                del session[cas_token_session_key]

        logger.debug('Redirecting to: {0}'.format(redirect_url))

        return redirect(redirect_url)

    @get()
    def logout(self, session: Session):
        """
        When the user accesses this route they are logged out.
        """

        cas_username_session_key = settings['CAS_USERNAME_SESSION_KEY']
        cas_attributes_session_key = settings['CAS_ATTRIBUTES_SESSION_KEY']

        if cas_username_session_key in session:
            del session[cas_username_session_key]

        if cas_attributes_session_key in session:
            del session[cas_attributes_session_key]

        if settings['CAS_AFTER_LOGOUT'] is not None:
            redirect_url = create_cas_logout_url(
                settings['CAS_SERVER'],
                settings['CAS_LOGOUT_ROUTE'],
                settings['CAS_AFTER_LOGOUT'])
        else:
            redirect_url = create_cas_logout_url(
                settings['CAS_SERVER'],
                settings['CAS_LOGOUT_ROUTE'])

        logger.debug('Redirecting to: {0}'.format(redirect_url))
        return redirect(redirect_url)


def validate(ticket, login_url, session: Session):
    """
    Will attempt to validate the ticket. If validation fails, then False
    is returned. If validation is successful, then True is returned
    and the validated username is saved in the session under the
    key `CAS_USERNAME_SESSION_KEY` while tha validated attributes dictionary
    is saved under the key 'CAS_ATTRIBUTES_SESSION_KEY'.
    """

    cas_username_session_key = settings['CAS_USERNAME_SESSION_KEY']
    cas_attributes_session_key = settings['CAS_ATTRIBUTES_SESSION_KEY']

    logger.debug("validating token {0}".format(ticket))

    cas_validate_url = create_cas_validate_url(
        settings['CAS_SERVER'],
        settings['CAS_VALIDATE_ROUTE'],
        login_url,
        ticket)

    logger.debug("Making GET request to {0}".format(cas_validate_url))

    xml_from_dict = {}
    isValid = False

    try:
        xmldump = urlopen(cas_validate_url).read().strip().decode('utf8', 'ignore')
        xml_from_dict = parse(xmldump)
        isValid = True if "cas:authenticationSuccess" in xml_from_dict["cas:serviceResponse"] else False
    except ValueError:
        logger.error("CAS returned unexpected result")

    if isValid:
        logger.debug("valid")
        xml_from_dict = xml_from_dict["cas:serviceResponse"]["cas:authenticationSuccess"]
        username = xml_from_dict["cas:user"]
        attributes = xml_from_dict["cas:attributes"]

        if "cas:memberOf" in attributes:
            attributes["cas:memberOf"] = attributes["cas:memberOf"].lstrip('[').rstrip(']').split(',')
            for group_number in range(0, len(attributes['cas:memberOf'])):
                attributes['cas:memberOf'][group_number] = attributes['cas:memberOf'][group_number].lstrip(' ').rstrip(' ')

        session[cas_username_session_key] = username
        session[cas_attributes_session_key] = attributes
    else:
        logger.debug("invalid")

    return isValid
