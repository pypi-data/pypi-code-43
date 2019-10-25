#
# Copyright (c) 2014, 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# from xlrd import xldate_as_tuple, empty_cell
# from xlrd import XL_CELL_EMPTY, XL_CELL_NUMBER, XL_CELL_TEXT, XL_CELL_DATE
import datetime
from xlwt import Workbook, XFStyle
from coils.foundation import StandardXML
from coils.core.logic import ActionCommand

XF_DEFAULT_STYLE = None
XF_DATE_STYLE = None
XF_DATETIME_STYLE = None


def default_column_style(val):
    """
    Return the appropriate XFStyle for the value type

    Note that StandardXML always returns a datetime, never a date, so without
    some coercion the the XLS will style all values as datetimes.
    """

    global XF_DEFAULT_STYLE
    global XF_DATE_STYLE
    global XF_DATETIME_STYLE

    if XF_DEFAULT_STYLE is None:

        XF_DEFAULT_STYLE = XFStyle()

        XF_DATE_STYLE = XFStyle()
        XF_DATE_STYLE.num_format_str = 'YYYY-MM-DD'

        XF_DATETIME_STYLE = XFStyle()
        XF_DATETIME_STYLE.num_format_str = 'YYYY-MM-DD HH:mm'

    """
    Test for datetime type FIRST as a datetime is a date, so if you test for
    date first you will not be able to tell the difference.
    """
    if isinstance(val, (datetime.datetime, )):
        return XF_DATETIME_STYLE
    elif isinstance(val, (datetime.date, )):
        return XF_DATE_STYLE

    # TODO: should there be a default format for float values?

    # No style, probably just a string
    return XF_DEFAULT_STYLE


class XMLToXLSAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "xml-to-xls"
    __aliases__ = ['xmlToXlsAction', 'xmlToXls', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/vnd.ms-excel'

    def open_workbook(self, rfile):
        book = Workbook(style_compression=2)
        sheet = book.add_sheet('Sheet 1')
        return book, sheet

    def write_first_row(self, sheet):
        index = dict()
        counter = 0
        for keys, fields, in StandardXML.Read_Rows(handle=self.rfile, ):
            for key in keys:
                index[key] = counter
                counter += 1
            for field in fields:
                index[field] = counter
                counter += 1
            break
        for key, value, in index.items():
            sheet.row(0).write(value, key)
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)
        return index

    def write_rows_to_sheet(self, sheet, index,):
        counter = 0
        xls_row = 0
        for keys, fields, in StandardXML.Read_Rows(handle=self.rfile, ):
            counter += 1
            if (self._stop_at) and (counter > self._stop_at):
                self.log_message(
                    'breaking at row {0}'.format(counter, ),
                    category='debug',
                )
                break
            if (self._skip_until) and (counter < self._skip_until):
                continue
            # TODO: log the counter of the first row
            if not xls_row:
                self.log_message(
                    'starting export at row {0}'.format(counter, ),
                    category='debug',
                )
            xls_row += 1
            if not(counter % 5000):
                self.gong()  # gong every 5,000 records
            for key, value, in keys.items():
                if isinstance(value, basestring):
                    value = value.strip()
                    if len(value) > 32767:
                        self.log_message(
                            'long text value in row {0} column "{1}" truncated'
                            .format(counter, key, ),
                            category='warn',
                        )
                        value = value[0:32767]
                sheet.row(xls_row).write(
                    index[key], value, default_column_style(value),
                )
            for key, value, in fields.items():
                if isinstance(value, basestring):
                    value = value.strip()
                    if len(value) > 32767:
                        self.log_message(
                            'long text value in row {0} column "{1}" truncated'
                            .format(counter, key, ),
                            category='warn',
                        )
                        value = value[0:32767]
                sheet.row(xls_row).write(
                    index[key], value, default_column_style(value),
                )

    def close_workbook(self, book):
        book.save(self.wfile)

    def do_action(self):
        table_name, format_name, format_class, = \
            StandardXML.Read_ResultSet_Metadata(self.rfile)
        book, sheet, = self.open_workbook(rfile=self.rfile, )
        index = self.write_first_row(sheet=sheet, )
        self.write_rows_to_sheet(
            sheet=sheet,
            index=index,
        )
        sheet.flush_row_data()
        self.close_workbook(book=book, )

    def parse_action_parameters(self):

        self._skip_until = int(
            self.action_parameters.get('skipUntil', '0').strip()
        )
        self._stop_at = int(
            self.action_parameters.get('stopAt', '0').strip()
        )
