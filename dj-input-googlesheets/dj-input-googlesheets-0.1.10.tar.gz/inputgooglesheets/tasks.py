from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def import_google_spreadsheet(spreadsheet_pk):
    from .models import Spreadsheet
    from .utils import Utils
    try:
        spreadsheet = Spreadsheet.objects.get(pk=spreadsheet_pk)
        logger.info("Starting import spreadsheet {}".format(spreadsheet_pk))
    except Spreadsheet.DoesNotExist:
        logger.warn("Import spreadsheet {} failed. It does not exist.".format(spreadsheet_pk))
    count = Utils.import_to_input_flow(spreadsheet)
    logger.info("Finished importing spreadsheet {}: {} rows imported".format(spreadsheet_pk, count))
