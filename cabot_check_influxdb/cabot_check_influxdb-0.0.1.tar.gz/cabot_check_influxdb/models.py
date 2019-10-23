from influxdb import InfluxDBClient

from django.db import models

from cabot.cabotapp.models import StatusCheck, StatusCheckResult


class InfluxdbStatusCheck(StatusCheck):
    check_name = 'influxdb'
    edit_url_name = 'update-influxdb-check'
    duplicate_url_name = 'duplicate-influxdb-check'
    icon_class = 'glyphicon-fire'
    host = models.TextField(
        help_text='Host influxdb.',
    )
    port = models.TextField(
        help_text='port influxdb.',
    )
    database = models.TextField(
        help_text='database to check.',
    )
    query = models.TextField(
        help_text='Query to execute.',
    )

    def _run(self):
        result = StatusCheckResult(status_check=self)

        try:
            client = InfluxDBClient(host='%s', port=%s) % (host, port)
            db = client.switch_database('%s') % (database)
            _query = db.query('%') % (query)
        except Exception as e:
            result.error = u"{} {} {}".format(e.message, self.host, self.port)
            result.succeeded = False
        else:
            result.succeeded = True

        return result
