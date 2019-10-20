class SchemazerConfig:
    HOST = 'localhost'
    ERROR_HTTP_CODE = 200

    HTTP_SCHEMA = 'http'
    VERSION = 'schemazer'
    PROJECT_NAME = 'Unknown'

    DOCUMENTATION_PATH = '/documentation'
    DOCUMENTATION_LOGIN_PAGE_PATH = '/'
    DOCUMENTATION_LOGOUT_PAGE_PATH = '/logout'

    AUTH_LOGIN = 'admin'
    AUTH_PWD = 'secret'
    AUTH_ACCESS_TOKEN = None
    AUTH_COOKIE_TTL = 60 * 60
    AUTH_COOKIE_PARAMETER = 'token'
