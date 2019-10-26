from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task
from redis import StrictRedis
import redis_lock
from django.conf import settings


logger = logging.getLogger(__name__)

try:
    redis_conn = StrictRedis(**settings.REDIS_LOCK_CONN)
except AttributeError:
    redis_conn = StrictRedis()
LOCK_KEY = '744ed748-7685-41ca-a714-f0bfb6db0b80:{}'


@shared_task
def start_import(spreadsheet_pk):
    from .models import Spreadsheet
    from .utils import Utils
    lock_key = LOCK_KEY.format(spreadsheet_pk)
    with redis_lock.Lock(redis_conn, lock_key):
        try:
            spreadsheet = Spreadsheet.objects.get(pk=spreadsheet_pk)
            if not spreadsheet.enabled:
                logger.info("Could not import disabled spreadsheet: {}".format(spreadsheet_pk))
                return
            logger.info("Continue import spreadsheet: {}".format(spreadsheet_pk))
        except Spreadsheet.DoesNotExist:
            logger.warn("Import spreadsheet {} failed. It does not exist.".format(spreadsheet_pk))
        count = Utils.start_import(spreadsheet)
        logger.info("Finished importing spreadsheet {}: {} rows imported".format(spreadsheet_pk, count))


@shared_task
def continue_import(spreadsheet_pk):
    from .models import Spreadsheet
    from .utils import Utils
    lock_key = LOCK_KEY.format(spreadsheet_pk)
    with redis_lock.Lock(redis_conn, lock_key):
        try:
            spreadsheet = Spreadsheet.objects.get(pk=spreadsheet_pk)
            if not spreadsheet.enabled:
                logger.info("Could not import disabled spreadsheet: {}".format(spreadsheet_pk))
                return
            logger.info("Continue import spreadsheet: {}".format(spreadsheet_pk))
        except Spreadsheet.DoesNotExist:
            logger.warn("Import spreadsheet {} failed. It does not exist.".format(spreadsheet_pk))
        count = Utils.continue_import(spreadsheet)
        logger.info("Finished importing spreadsheet {}: {} rows imported".format(spreadsheet_pk, count))


@shared_task
def import_all_google_spreadsheets():
    from .models import Spreadsheet
    for spreadsheet in Spreadsheet.objects.filter(enabled=True, automatically_imported=True):
        continue_import.delay(spreadsheet.pk)
