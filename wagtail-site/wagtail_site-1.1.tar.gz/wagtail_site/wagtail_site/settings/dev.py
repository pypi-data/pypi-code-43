from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+xa+_d4nw#-%v&y6xobv+%z)+qy%f#npo0fhh+5%m=h@k4h0f3'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
