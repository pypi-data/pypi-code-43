from django.conf import settings

from .helpers import Choices

STATES = Choices(
    ('DRAFT', 100, 'Draft'),
    ('SUBMITTED', 200, 'Submitted'),
    ('ACCEPTED', 300, 'Accepted'),
    ('REFUSED', -1, 'Refused'),
    ('CANCELLED', -100, 'Cancelled'),
    ('MISSING', 0, 'Missing'),
)
STATES.add_subset('MANUAL', (
    'DRAFT',
    'SUBMITTED',
    'ACCEPTED',
    'REFUSED',
    'CANCELLED',
))

STATES = getattr(settings, 'STATES', STATES)

TERRA_APPLIANCE_SETTINGS = getattr(settings, 'TERRA_APPLIANCE_SETTINGS', {})
FRONT_URL = getattr(settings, 'FRONT_URL', 'http://localhost:3000')
HOSTNAME = getattr(settings, 'HOSTNAME', 'http://localhost:8000')

MEDIA_ACCEL_REDIRECT = getattr(settings, 'MEDIA_ACCEL_REDIRECT', False)
