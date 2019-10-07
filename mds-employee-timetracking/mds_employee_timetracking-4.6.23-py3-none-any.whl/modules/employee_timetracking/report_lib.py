# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.modules.company import CompanyReport
from trytond.pool import Pool
import string, unicodedata
from datetime import date, datetime, time, timedelta
from .tools import fmttimedelta, format_float

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)


# a dirty hack --> should go to genshi
# from: account_payment_sepa.payment.py:
# XXX fix: https://genshi.edgewall.org/ticket/582
from genshi.template.astutil import ASTCodeGenerator, ASTTransformer
if not hasattr(ASTCodeGenerator, 'visit_NameConstant'):
    def visit_NameConstant(self, node):
        if node.value is None:
            self._write('None')
        elif node.value is True:
            self._write('True')
        elif node.value is False:
            self._write('False')
        else:
            raise Exception("Unknown NameConstant %r" % (node.value,))
    ASTCodeGenerator.visit_NameConstant = visit_NameConstant
if not hasattr(ASTTransformer, 'visit_NameConstant'):
    # Re-use visit_Name because _clone is deleted
    ASTTransformer.visit_NameConstant = ASTTransformer.visit_Name


class ReportLib(CompanyReport):
    """ extend report
    """
    @classmethod
    def get_context(cls, records, data):
        report_context = super(ReportLib, cls).get_context(records, data)
        report_context['islastitem'] = cls.is_last_item
        report_context['format_time'] = cls.formattime
        report_context['format_timedelta'] = cls.formattimedelta
        report_context['format_float'] = cls.formatfloat
        return report_context

    @classmethod
    def clean_filename(cls, filename, whitelist=valid_filename_chars, replace=' '):
        """ replace/remove not compatible chars
        """
        for r in replace:
            filename = filename.replace(r, '_')
        
        # keep only valid ascii chars
        cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
        return ''.join(c for c in cleaned_filename if c in whitelist)

    @classmethod
    def formattimedelta(cls, deltaval, noplussign=False):
        """ format time delta
        """
        return fmttimedelta(deltaval, noplussign)

    @classmethod
    def formatfloat(cls, numbr, groups=False, stripzeros=False, numdec=2):
        """ format float/decimal
        """
        return format_float(numbr=numbr, groups=groups, stripzeros=stripzeros, numdec=numdec)

    @classmethod
    def formattime(cls, timeval, timezone=None):
        """ format time value from datetime
        """
        AccountRule = Pool().get('employee_timetracking.accountrule')
        
        if isinstance(timeval, type(datetime(2010, 1, 1, 10, 0, 0))):
            if isinstance(timezone, type(None)):
                return timeval.strftime('%H:%M')
            else:
                return AccountRule.get_localtime(timeval, timezone).strftime('%H:%M')
        elif isinstance(timeval, type(time(10, 0, 0))):
            return timeval.strftime('%H:%M')
        else :
            return ''

    @classmethod
    def is_last_item(cls, liste, item):
        """ detect last item in list
        """
        if liste[-1].id == item.id:
            return True
        else :
            return False

    @classmethod
    def execute(cls, ids, data):
        """ change filename
        """
        ExpObj = Pool().get(data['model'])(data['id'])
        (ext1, cont1, dirprint, titel) = super(ReportLib, cls).execute(ids, data)
        title = '%s-%s-%s' % (
            date.today().strftime('%Y%m%d'), 
            getattr(cls, 'reportfname', data['model'].split('.')[1]),
            ExpObj.rec_name)
        return (ext1, cont1, dirprint, cls.clean_filename(filename=title))

# end ReportLib
