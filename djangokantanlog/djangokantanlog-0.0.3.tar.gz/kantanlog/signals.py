from logging import getLogger
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save
from .middlewares import get_username


logger = getLogger(__name__)
_labels = getattr(
    settings,
    'KLOG_TARGET_APP_LABELS',
    (),
)


@receiver(pre_save)
def log_cbyuby(sender, **kwargs):
    if kwargs['raw']:
        return
    instance = kwargs['instance']
    if not (instance._meta.app_label in _labels):
        return
    username = get_username()
    if not username:
        logger.debug('Username value is falsy: %s', username)

    if hasattr(instance, 'created_by') and not getattr(instance, 'created_by'):
        setattr(instance, 'created_by', username)
    if hasattr(instance, 'updated_by'):
        setattr(instance, 'updated_by', username)
