import datetime
import json
import pytz
import re
import six
import sys
import traceback

from seeq.sdk43 import *
from seeq.sdk43.rest import ApiException

from IPython.core.display import display, HTML, clear_output

import pandas as pd
import numpy as np

DEFAULT_DATASOURCE_NAME = 'Seeq Data Lab'
DEFAULT_DATASOURCE_CLASS = 'Seeq Data Lab'
DEFAULT_DATASOURCE_ID = 'Seeq Data Lab'
DEFAULT_WORKBOOK_PATH = 'Data Lab >> Data Lab Analysis'
DEFAULT_SEARCH_PAGE_SIZE = 100
DEFAULT_PULL_PAGE_SIZE = 1000000
DEFAULT_PUT_SAMPLES_AND_CAPSULES_BATCH_SIZE = 100000


class DependencyNotFound(Exception):

    def __init__(self, identifier, message=None):
        self.identifier = identifier
        self.message = message

    def __repr__(self):
        return '%s%s' % (self.identifier, '\n' + self.message if self.message else '')


def present(row, column):
    return (column in row) and \
           (row[column] is not None) and \
           (not isinstance(row[column], float) or not pd.isna(row[column]))


def get(row, column, default=None):
    return row[column] if present(row, column) else default


def get_timings(http_headers):
    output = dict()
    for header, cast in [('Server-Meters', int), ('Server-Timing', float)]:
        server_meters_string = http_headers[header]
        server_meters = server_meters_string.split(',')
        for server_meter_string in server_meters:
            server_meter = server_meter_string.split(';')
            if len(server_meter) < 3:
                continue

            dur_string = cast(server_meter[1].split('=')[1])
            desc_string = server_meter[2].split('=')[1].replace('"', '')

            output[desc_string] = dur_string

    return output


def format_exception(e=None):
    exception_type = None
    tb = None
    if e is None:
        exception_type, e, tb = sys.exc_info()

    if isinstance(e, ApiException):
        content = ''
        if e.reason and len(e.reason.strip()) > 0:
            if len(content) > 0:
                content += ' - '
            content += e.reason

        if e.body:
            # noinspection PyBroadException
            try:
                body = json.loads(e.body)
                if len(content) > 0:
                    content += ' - '
                content += body['statusMessage']
            except BaseException:
                pass

        return '(%d) %s' % (e.status, content)

    else:
        if tb is not None:
            return traceback.format_exception(exception_type, e, tb)
        else:
            return str(e)


GUID_REGEX = r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}'


def is_guid(s):
    return isinstance(s, str) and re.match(GUID_REGEX, sanitize_guid(s))


def sanitize_guid(g):
    return g.upper()


def validate_timezone_arg(tz):
    if tz is not None:
        try:
            pd.to_datetime('2019-01-01T00:00:00.000Z').tz_convert(tz)

        except pytz.exceptions.UnknownTimeZoneError:
            raise RuntimeError('Unknown timezone "%s". Acceptable timezones:\n%s' % (tz, '\n'.join(pytz.all_timezones)))


def validate_errors_arg(errors):
    if errors not in ['raise', 'catalog']:
        raise RuntimeError("errors argument must be either 'raise' or 'catalog'")


def none_to_nan(v):
    return np.nan if v is None else v


def ensure_unicode(o):
    if isinstance(o, six.binary_type):
        return six.text_type(o, 'utf-8', errors='replace')
    else:
        return o


def timer_start():
    return datetime.datetime.now()


def timer_elapsed(timer):
    return datetime.datetime.now() - timer


def convert_to_timestamp(unix_timestamp_in_ns, tz):
    return convert_timestamp_timezone(none_to_nan(pd.Timestamp(unix_timestamp_in_ns)), tz)


def convert_timestamp_timezone(timestamp, tz):
    if pd.isna(timestamp):
        return timestamp

    timestamp = timestamp.tz_localize('UTC')
    return timestamp.tz_convert(tz) if tz else timestamp


def display_supports_html():
    # noinspection PyBroadException
    try:
        # noinspection PyUnresolvedReferences
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str:
            return True
        if 'terminal' in ipy_str:
            return False

    except:
        return False


def ipython_clear_output(wait=False):
    clear_output(wait)


def ipython_display(*objs, include=None, exclude=None, metadata=None, transient=None, display_id=None, **kwargs):
    display(*objs, include=include, exclude=exclude, metadata=metadata, transient=transient,
            display_id=display_id, **kwargs)


def get_data_lab_datasource_input():
    datasource_input = DatasourceInputV1()
    datasource_input.name = DEFAULT_DATASOURCE_CLASS
    datasource_input.description = 'Signals, conditions and scalars from Seeq Data Lab.'
    datasource_input.datasource_class = DEFAULT_DATASOURCE_CLASS
    datasource_input.datasource_id = DEFAULT_DATASOURCE_ID
    datasource_input.stored_in_seeq = True
    datasource_input.additional_properties = [ScalarPropertyV1(name='Expect Duplicates During Indexing', value=True)]
    return datasource_input


def regex_from_query_fragment(query_fragment, contains=True):
    if query_fragment.startswith('/') and query_fragment.endswith('/'):
        regex = query_fragment[1:-1]
    else:
        regex = query_fragment.replace('.', r'\.').replace('?', '.').replace('*', '.*')

        if contains and not regex.startswith('.*') and not regex.endswith('.*'):
            regex = '.*' + regex + '.*'

    return regex


def does_query_fragment_match(query_fragment, string, contains=True):
    regex = regex_from_query_fragment(query_fragment, contains=contains)
    return re.fullmatch(regex, string, re.IGNORECASE) is not None


def get_workbook_type(workbook_output_data):
    if not workbook_output_data:
        return 'Analysis'

    # noinspection PyBroadException
    try:
        data = json.loads(workbook_output_data)
    except BaseException:
        return 'Analysis'

    if 'isReportBinder' in data and data['isReportBinder']:
        return 'Topic'
    else:
        return 'Analysis'


class Status:
    RUNNING = 0
    SUCCESS = 1
    FAILURE = 2
    CANCELED = 3

    def __init__(self, quiet=False):
        self.quiet = quiet
        self.df = pd.DataFrame()
        self.timer = timer_start()
        self.last_display_status_message = None

    def metrics(self, d):
        self.df = pd.DataFrame(d).transpose()

    def update(self, message, status):
        if self.quiet:
            return

        if not display_supports_html():
            if message != self.last_display_status_message:
                text = re.sub(r'</?[^>]+>', '', message)
                display(text)
                self.last_display_status_message = message
            return

        ipython_clear_output(wait=True)

        display_df = self.df
        if len(self.df) > 20 and 'Result' in self.df.columns:
            display_df = self.df[~self.df['Result'].isin(['Queued', 'Success'])]

        if status == Status.RUNNING:
            color = '#EEEEFF'
        elif status == Status.SUCCESS:
            color = '#EEFFEE'
        else:
            color = '#FFEEEE'

        style = 'background-color: %s;' % color
        html = '<div style="%s">%s</div>' % (
            style + 'text-align: left;', message.replace('\n', '<br>'))

        html += '<table>'
        html += '<tr><td style="%s"></td>' % style

        for col in display_df.columns:
            html += '<td style="%s">%s</td>' % (style, col)

        html += '</tr>'

        for index, row in display_df.iterrows():
            html += '<tr style="%s">' % style
            html += '<td>%s</td>' % index
            for cell in row:
                if isinstance(cell, datetime.timedelta):
                    hours, remainder = divmod(cell.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    html += '<td>{:02}:{:02}:{:02}.{:02}</td>'.format(int(hours), int(minutes), int(seconds),
                                                                      int((cell.microseconds + 5000) / 10000))
                else:
                    html += '<td>%s</td>' % cell
            html += '</tr>'

        html += '</table>'

        display(HTML(html))

    def get_timer(self):
        return timer_elapsed(self.timer)

    def reset_timer(self):
        self.timer = timer_start()

    def exception(self, e):
        if isinstance(e, KeyboardInterrupt):
            self.df['Result'] = 'Canceled'
            status_message = 'Canceled'
            status_code = Status.CANCELED
        else:
            status_message = 'Error encountered, scroll down to view'
            status_code = Status.FAILURE

        self.update(status_message, status_code)

    @staticmethod
    def validate(status, quiet=False):
        """
        :param status: An already-instantiated Status object
        :type status: Status
        :param quiet: If True, suppresses output to Jupyter/console
        :type quiet: bool
        :rtype Status
        :return: The already-instantiated Status object passed in, or a newly-instantiated Status object
        """
        if status is None:
            status = Status(quiet=quiet)

        if not isinstance(status, Status):
            raise TypeError(f'Argument status must be of type Status, not {type(status)}')

        return status
