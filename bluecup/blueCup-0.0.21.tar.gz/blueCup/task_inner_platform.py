from __future__ import absolute_import

import traceback
from typing import Dict, Optional, Tuple, Any

from celery import chain
from celery import group
from celery import signature
from nezha.file import Dir
from nezha.uexcel import Excel
from nezha.ustring import is_invalid_str, unique_id
from nezha.errors import IncomingDataError
from nezha.errors import RequestFailed
from muzha.booldata.hz_risk_model import batch_test
from muzha.booldata.multi_platforms_v2 import ApplyDetail
from muzha.booldata.multi_platforms_v2 import LiabilitiesDetails
from muzha.booldata.multi_platforms_v2 import OverdueDetail
from muzha.booldata.multi_platforms_v2 import RepaymentDetail
from muzha.booldata.multi_platforms_v2 import batch_test_apply_detail
from muzha.booldata.multi_platforms_v2 import batch_test_liabilities_detail
from muzha.booldata.multi_platforms_v2 import batch_test_overdue_detail
from muzha.booldata.multi_platforms_v2 import batch_test_repayment_detail
from nezha.file import File

from .celery import app
from .task_notification import send_email_attach, emailAbout, send_dingding_text, dingUrl

"""
celery task batch_test_huizumodel remote call example:

from celery import Celery

app = Celery('async_task')
app.config_from_object('async_task.conf')
app.add_defaults({
    'BROKER_URL': f'redis://{host}:{port}/{db}',
    'CELERY_RESULT_BACKEND': f'redis://{host}:{port}/{db}',
})

if __name__ == '__main__':
    from gitignore.batch_test.mainv3 import BOOLDATA_ACCOUNT
    from pysubway.utils.file import File
    app.send_task('batch_test_huizumodel', (BOOLDATA_ACCOUNT,
                                            'prod',
                                            '01b20490-4a1e-11e9-9eb7-247703d210dc',
                                            'name,phone,idcard\n朱**,180****622,3506261*****511',
                                            File.this_dir(__file__)))
"""


def len_biz_data(biz_data: str) -> int:
    # 1 stands for columns
    return len(biz_data.split('\n')) - 1


def add_header_for_biz_data(biz_data: str, header: Tuple[str, ...] = ('name', 'phone', 'idcard')) -> str:
    """
    header default queue: ('name', 'phone', 'idcard')
    :param biz_data:
    :return:
    """
    return biz_data if biz_data.startswith('name') else '\n'.join((','.join(header),) + (biz_data,))


@app.task(name='batch_test_huizumodel', bind=True, autoretry_for=(RequestFailed,), retry_kwargs={'max_retries': 3})
def batch_test_huizumodel(self: Any, account_info: Dict[str, str],
                          env: str,
                          company_uuid: str,
                          biz_data: str,
                          current_dir: str,
                          raise_failed_exception: bool = True,
                          email_about: Optional[emailAbout] = None,
                          ding_url: Optional[dingUrl] = None) -> Dict:
    """
    :param account_info:
    :param env:
    :param company_uuid:
    :param biz_data:
    :param current_dir:
    :param raise_failed_exception:
    :return:
    """
    from .task_base import TaskBase, CODE_INCOMING_DATA_ERROR
    print('batch_test_huizumodel incoming_data', locals())
    biz_data = add_header_for_biz_data(biz_data)
    if is_invalid_str(biz_data):
        return TaskBase.task_result({'is_succeed': False, 'msg': '提交数据有误'})
    output = File.join_path(current_dir, f'{unique_id()}.xlsx')
    excel_ins = Excel.prepare_file(biz_data).read()
    account = account_info.copy()
    account['company_uuid'] = company_uuid
    error_log = File.join_path(current_dir, 'log', File(output).pure_name)
    try:
        if ding_url:
            print('ding_url is', ding_url)
            ding_url = dingUrl._make(ding_url)
        batch_test(excel_ins.dataframe, account,
                   output, names=tuple(excel_ins.header), error_log=error_log,
                   raise_failed_exception=raise_failed_exception,
                   env=env)
        if not email_about:
            return TaskBase.task_result({'is_succeed': True, 'data': output})
        if email_about:
            email_about = emailAbout._make(email_about)
            send_email_attach.delay(email_about.mail_user,
                                    email_about.mail_pass,
                                    email_about.title,
                                    email_about.content,
                                    output,
                                    email_about.receivers)
            if email_about.specified_receivers:
                send_email_attach.delay(email_about.mail_user,
                                        email_about.mail_pass,
                                        email_about.title,
                                        email_about.content,
                                        output,
                                        email_about.specified_receivers)
        msg = f'{email_about.title}\n{email_about.content}\n测试了{len_biz_data(biz_data)}条.'
        if ding_url:
            send_dingding_text.delay(ding_url.ding_msg, msg)
        return TaskBase.task_result({'is_succeed': True, 'data': output})
    except IncomingDataError as e:
        traceback.print_exc()
        except_info = traceback.format_exc()
        if ding_url:
            send_dingding_text.delay(ding_url.ding_exception, except_info)
        return {'is_succeed': False, 'msg': except_info, 'msg_code': CODE_INCOMING_DATA_ERROR}
    except Exception as e:
        if ding_url:
            send_dingding_text.delay(ding_url.ding_exception, traceback.format_exc())
        traceback.print_exc()
        raise RequestFailed(e)


@app.task(name='multi_v2_batch_test_liabilities_detail', bind=True, autoretry_for=(RequestFailed,),
          retry_kwargs={'max_retries': 3})
def multi_v2_batch_test_liabilities_detail(self: Any, input: str,
                                           input_is_str: bool,
                                           account: Dict[str, str],
                                           output_liabilities_detail: str,
                                           names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                                           raise_failed_exception: bool = True,
                                           error_log: Optional[str] = None) -> None:
    batch_test_liabilities_detail(input,
                                  input_is_str,
                                  account,
                                  output_liabilities_detail,
                                  names=names,
                                  raise_failed_exception=raise_failed_exception,
                                  error_log=error_log)


@app.task(name='multi_v2_batch_test_repayment_detail', bind=True, autoretry_for=(RequestFailed,),
          retry_kwargs={'max_retries': 3})
def multi_v2_batch_test_repayment_detail(self: Any, input: str,
                                         input_is_str: bool,
                                         account: Dict[str, str],
                                         output_repayment_detail: str,
                                         names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                                         raise_failed_exception: bool = True,
                                         error_log: Optional[str] = None) -> None:
    batch_test_repayment_detail(input,
                                input_is_str,
                                account,
                                output_repayment_detail,
                                names=names,
                                raise_failed_exception=raise_failed_exception,
                                error_log=error_log)


@app.task(name='multi_v2_batch_test_overdue_detail', bind=True, autoretry_for=(RequestFailed,),
          retry_kwargs={'max_retries': 3})
def multi_v2_batch_test_overdue_detail(self: Any, input: str,
                                       input_is_str: bool,
                                       account: Dict[str, str],
                                       output_dir_overdue_detail: str,
                                       names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                                       raise_failed_exception: bool = True,
                                       error_log: Optional[str] = None) -> None:
    batch_test_overdue_detail(input,
                              input_is_str,
                              account,
                              output_dir_overdue_detail,
                              names=names,
                              raise_failed_exception=raise_failed_exception,
                              error_log=error_log)


@app.task(name='multi_v2_batch_test_apply_detail', bind=True, autoretry_for=(RequestFailed,),
          retry_kwargs={'max_retries': 3})
def multi_v2_batch_test_apply_detail(self: Any, input: str,
                                     input_is_str: bool,
                                     account: Dict[str, str],
                                     output_dir_apply_detail: str,
                                     names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                                     raise_failed_exception: bool = True,
                                     error_log: Optional[str] = None) -> None:
    batch_test_apply_detail(input,
                            input_is_str,
                            account,
                            output_dir_apply_detail,
                            names=names,
                            raise_failed_exception=raise_failed_exception,
                            error_log=error_log)


@app.task(name='zip_dir', bind=True, autoretry_for=(RequestFailed,), retry_kwargs={'max_retries': 3})
def zip_dir(self: Any, output_dir: str) -> str:
    """

    :param dir:
    :return:
    """
    print('zip_dir', '*' * 10, locals())
    dir = Dir(output_dir)
    return dir.zip()


@app.task(name='async_batch_test_email_notification', bind=True, autoretry_for=(RequestFailed,),
          retry_kwargs={'max_retries': 3})
def async_batch_test_email_notification(self: Any, msg: str,
                                        output: str,
                                        email_about: Optional[emailAbout] = None,
                                        ding_url: Optional[dingUrl] = None) -> None:
    print(f'[async_batch_test_email_notification] local ->{locals()}<-')
    if email_about:
        email_about = emailAbout._make(email_about)
        send_email_attach.delay(email_about.mail_user,
                                email_about.mail_pass,
                                email_about.title,
                                email_about.content,
                                output,
                                email_about.receivers)
        if email_about.specified_receivers:
            send_email_attach.delay(email_about.mail_user,
                                    email_about.mail_pass,
                                    email_about.title,
                                    email_about.content,
                                    output,
                                    email_about.specified_receivers)
    if ding_url:
        ding_url = dingUrl._make(ding_url)
        send_dingding_text.delay(ding_url.ding_msg, msg)


@app.task(name='multi_platforms_v2', bind=True, autoretry_for=(RequestFailed,), retry_kwargs={'max_retries': 3})
def multi_platforms_v2(self: Any,
                       input: str = '',
                       input_is_str: bool = True,
                       account: Optional[Dict[str, str]] = None,
                       output_dir: str = '',
                       names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                       raise_failed_exception: bool = True,
                       error_log: Optional[str] = None,
                       email_about: Optional[emailAbout] = None,
                       ding_url: Optional[dingUrl] = None) -> None:
    print('multi_platforms_v2', locals())
    dir = Dir(output_dir)
    dir.mkdir()
    print('multi_platforms_v2 mkdir', '*' * 10)
    if not dir.is_dir():
        raise ValueError(f'output_dir {output_dir} must be dir')
    input = add_header_for_biz_data(input)
    output_liabilities_detail = File.join_path(output_dir, LiabilitiesDetails.interface_chinese_name + '.xlsx')
    output_repayment_detail = File.join_path(output_dir, RepaymentDetail.interface_chinese_name + '.xlsx')
    output_dir_overdue_detail = File.join_path(output_dir, OverdueDetail.interface_chinese_name + '.xlsx')
    output_dir_apply_detail = File.join_path(output_dir, ApplyDetail.interface_chinese_name + '.xlsx')
    print('multi_platforms_v2 generate files', '*' * 10)
    group_batch_test = group(multi_v2_batch_test_liabilities_detail.si(input,
                                                                       input_is_str,
                                                                       account,
                                                                       output_liabilities_detail,
                                                                       names=names,
                                                                       raise_failed_exception=raise_failed_exception,
                                                                       error_log=error_log),
                             multi_v2_batch_test_repayment_detail.si(input,
                                                                     input_is_str,
                                                                     account,
                                                                     output_repayment_detail,
                                                                     names=names,
                                                                     raise_failed_exception=raise_failed_exception,
                                                                     error_log=error_log),
                             multi_v2_batch_test_overdue_detail.si(input,
                                                                   input_is_str,
                                                                   account,
                                                                   output_dir_overdue_detail,
                                                                   names=names,
                                                                   raise_failed_exception=raise_failed_exception,
                                                                   error_log=error_log),
                             multi_v2_batch_test_apply_detail.si(input,
                                                                 input_is_str,
                                                                 account,
                                                                 output_dir_apply_detail,
                                                                 names=names,
                                                                 raise_failed_exception=raise_failed_exception,
                                                                 error_log=error_log)
                             )
    print('multi_platforms_v2 group_batch_test generate', '*' * 10)
    if email_about:
        email_about = emailAbout._make(email_about)
        msg = f'{email_about.title}\n{email_about.content}\n测试了{len_biz_data(input)}条.'
    else:
        raise ValueError(f'email_about {email_about} not exist')
    chain(signature(group_batch_test),
          zip_dir.si(output_dir),
          async_batch_test_email_notification.si(msg,
                                                 dir.generate_zip_name(),
                                                 email_about=email_about,
                                                 ding_url=ding_url)
          ).delay()
    print('multi_platforms_v2 chain delay', '*' * 10)
