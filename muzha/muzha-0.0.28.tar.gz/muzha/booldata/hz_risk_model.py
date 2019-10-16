import json
from typing import Dict, Optional, Tuple, Any, Union, TextIO, List

import pandas as pd
from nezha import udict
from nezha.errors import IncomingDataError
from nezha.errors import RequestFailed
from nezha.file import File
from nezha.uexcel import Excel
from nezha.uexcel import Json2Excel
from nezha.ustring import is_invalid_str, unique_id

from .base import BoolDataBase

TEMPLATE_V01 = 'template_hz_risk_model.xlsx'
TEMPLATE_V02 = 'template_hz_risk_model_v02.xlsx'
THIS_DIR = File.this_dir(__file__)


class HzRiskModel(BoolDataBase):
    service = 'hz_risk_model_service'
    mode = 'hz_risk_model_personal_credit_mode'
    df_default_header = ('姓名', '身份证号', '手机号', '综合评分', '审核建议', '命中风险标注', '年龄', '户籍', '手机号归属地',
                         '个人欺诈黑名单', '户籍地位于高风险集中地区', '法院失信名单', '犯罪通缉名单', '法院执行名单', '助学贷款欠费历史',
                         '信贷逾期名单', '高风险关注名单', '车辆租赁违约名单', '法院结案名单', '故意违章乘车名单', '欠税名单',
                         '欠税公司法人代表名单', '虚拟号码库', '通信小号库', '近12个月申请机构总数', '消费分期类申请机构数',
                         '网络贷款类申请机构数', '最近一次申请日期', '距离最近一次申请日期天数', '近1个月申请次数', '近3个月申请次数',
                         '近6个月申请次数', '近12个月申请次数', '近12个月放款机构总数', '消费分期类放款机构数', '网络贷款类放款机构数',
                         '最近一次放款日期', '距离最近一次放款天数', '近1个月放款次数', '近3个月放款次数', '近6个月放款次数',
                         '近1个月履约次数', '近1个月还款异常次数', '近12个月履约次数', '近12个月还款异常次数', '近6个月逾期机构总数',
                         '近6个月逾期总次数', '近6个月未结清逾期次数', '近6个月逾期总金额（元）', '逾期金额区间（元）', '逾期时间', '逾期时长',
                         '是否结清', '3个月身份证关联手机号数', '3个月手机号关联身份证数', '近7天申请查询总数', '近7天P2P平台',
                         '近7天信用卡', '近7天一般消费分期平台', '近7天大型消费金融公司', '近7天小额贷款公司', '近7天其他类型公司',
                         '近30天申请查询总数', '近30天P2P平台', '近30天信用卡', '近30天一般消费分期平台', '近30天大型消费金融公司',
                         '近30天小额贷款公司', '近30天其他类型公司', '近90天申请查询总数', '近90天P2P平台', '近90天信用卡',
                         '近90天一般消费分期平台', '近90天大型消费金融公司', '近90天小额贷款公司', '近90天其他类型公司', '法院信息')

    df_default_header_v2 = ('姓名', '身份证号', '手机号', '综合评分', '审核建议', '命中风险标注', '年龄', '户籍', '手机号归属地',
                            '个人欺诈黑名单', '户籍地位于高风险集中地区', '法院失信名单', '犯罪通缉名单', '法院执行名单', '助学贷款欠费历史',
                            '信贷逾期名单', '高风险关注名单', '车辆租赁违约名单', '法院结案名单', '故意违章乘车名单', '欠税名单',
                            '欠税公司法人代表名单', '虚拟号码库', '通信小号库', '近12个月申请机构总数', '消费分期类申请机构数',
                            '网络贷款类申请机构数', '最近一次申请日期', '距离最近一次申请日期天数', '近1个月申请次数', '近3个月申请次数',
                            '近6个月申请次数', '近12个月申请次数', '近12个月放款机构总数', '消费分期类放款机构数', '网络贷款类放款机构数',
                            '最近一次放款日期', '距离最近一次放款天数', '近1个月放款次数', '近3个月放款次数', '近6个月放款次数',
                            '近1个月履约次数', '近1个月还款异常次数', '近12个月履约次数', '近12个月还款异常次数', '近6个月逾期机构总数',
                            '近6个月逾期总次数', '近6个月未结清逾期次数', '近6个月逾期总金额（元）',
                            '逾期详情',
                            '3个月身份证关联手机号数', '3个月手机号关联身份证数', '近7天申请查询总数', '近7天P2P平台',
                            '近7天信用卡', '近7天一般消费分期平台', '近7天大型消费金融公司', '近7天小额贷款公司', '近7天其他类型公司',
                            '近30天申请查询总数', '近30天P2P平台', '近30天信用卡', '近30天一般消费分期平台', '近30天大型消费金融公司',
                            '近30天小额贷款公司', '近30天其他类型公司', '近90天申请查询总数', '近90天P2P平台', '近90天信用卡',
                            '近90天一般消费分期平台', '近90天大型消费金融公司', '近90天小额贷款公司', '近90天其他类型公司', '法院信息')

    @classmethod
    def generate_biz_data(cls, name: str, phone: str, ident_number: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        import pandas as pd
        pd.Series({'a': 1, 'b': 2, 'c': 3, }, index=['c', 'b', 'a', 'f'])
        return biz_data

    def set_biz_data(self, name: str, phone: str, ident_number: str) -> 'HzRiskModel':
        self.biz_data = self.generate_biz_data(name, phone, ident_number)
        return self


def batch_test(
        input: Union[str, pd.DataFrame, TextIO],
        account: Dict[str, str],
        output_file: str,
        template: str = File.join_path(THIS_DIR, TEMPLATE_V02),
        names: Optional[Tuple[str, ...]] = ('name', 'phone', 'idcard'),
        columns: Tuple[str, ...] = HzRiskModel.df_default_header_v2,
        skiprows: Union[int, Tuple[int, ...], None] = None,
        error_log: Optional[str] = None,
        header: Union[int, List[int], None] = 0,
        raise_failed_exception: bool = False,
        env: str = 'prod') -> None:
    """
    batch test HzRiskModel, read from excel -> request HzRiskModel -> save result to excel

    :param template: result is transferred excel as the template
    :param input: excel file or pd.DataFrame or TextIO. If input not str, you must specify param error_log
    :param account: booldata account
    :param output_file: xlsx file that saving booldata result
    :param names: input excel file header, you can adjust the sequence.
    :param columns: output_file columns header
    :param skiprows: strip rows
    :param error_log: records error comment item.
    :param header: input excel header, default first row in excel
    :param raise_failed_exception: if True, raise RequestFailed Exception when request booldata failed.
    :param exception_threshold: tolerate exception threshold in one request.
    :return: None
    """

    def write_error(error_log: str, msg: str) -> None:
        with open(error_log, mode='a') as f:
            print(msg)
            f.write(f"{msg}\n")

    discard_params = ['', None]
    error_log = error_log or File.join_path(File(input).dirname, '.'.join((File(input).pure_name, 'error_log')))
    template_excel = Json2Excel(template)
    input_excel: pd.DataFrame = Excel(input).read(names=names, skiprows=skiprows,
                                                  header=header).dataframe if isinstance(input, str) else input
    df_final = pd.DataFrame()
    try:
        guard_ins = HzRiskModel(account['rsa_prv_key'],
                                account['aes_key'],
                                account['company_uuid'],
                                url=HzRiskModel.urls[env])
        print('HzRiskModel.urls[env]', HzRiskModel.urls[env])
        for _, series in input_excel.iterrows():
            name, phone, idcard = str(series['name']), str(series['phone']), str(series['idcard'])
            print(f'It is running params: name {name}, phone {phone}, idcard {idcard}')
            copied = discard_params.copy()
            copied.extend((name, phone, idcard))
            if len(set(copied)) != len(copied):
                write_error(error_log, f"{series['idcard']},{series['name']},{series['phone']}")
                if raise_failed_exception:
                    raise IncomingDataError(f'name {name}, phone {phone}, idcard {idcard} has invalid params.')
                else:
                    continue
            ins_result = guard_ins.set_biz_data(name, str(phone), str(idcard)).request()
            if not guard_ins.is_succeed():
                if guard_ins.is_incoming_data_error():
                    raise ImportError(f'response {guard_ins.response}')
                if raise_failed_exception:
                    raise RequestFailed(f'{json.dumps(ins_result)}')
                print('error ins_result  ----> ', ins_result)
                write_error(error_log, f"{series['idcard']},{series['name']},{series['phone']}")
            df_parsed = template_excel.parse(ins_result, index=[0])
            df_final = df_final.append(df_parsed, ignore_index=True)
            # break
    finally:
        # update 19.07.23, if exception happens, the finally result will return.
        # update 19.07.26, Generate file if even df_final is empty.
        # The action may generate empty file but it's better the file is not exist.
        Json2Excel.to_excel(df_final, output_file, columns=columns)


def batch_test_used_web(account_info: Dict[str, str],
                        env: str,
                        company_uuid: str,
                        biz_data: str,
                        current_dir: str,
                        raise_failed_exception: bool = True,
                        attachment_filename: str = 'batch_test.xlsx'
                        ) -> Tuple[Any, str]:
    from pysubway.view import View
    if is_invalid_str(biz_data):
        raise IncomingDataError('提交数据有误')
    output = File.join_path(current_dir, f'{unique_id()}.xlsx')
    excel_ins = Excel.prepare_file(biz_data).read()
    account = account_info.copy()
    account['company_uuid'] = company_uuid
    error_log = File.join_path(current_dir, 'log', File(output).pure_name)
    batch_test(excel_ins.dataframe, account,
               output, names=tuple(excel_ins.header), error_log=error_log,
               raise_failed_exception=raise_failed_exception,
               env=env)
    return View.response.send_file(output,
                                   as_attachment=True,
                                   attachment_filename=attachment_filename), output


if __name__ == '__main__':
    from gitignore import BOOLDATA_ACCOUNT

    file = '/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/200zu.csv'
    output = '/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/virtualenv_phone_result.xlsx'
    # 有表头
    batch_test(file,
               BOOLDATA_ACCOUNT,
               output,
               skiprows=None,
               names=('name', 'phone', 'idcard'),
               header=0,
               raise_failed_exception=True)
    # 无表头
    # batch_test(file,
    #            BOOLDATA_ACCOUNT,
    #            output,
    #            skiprows=None,
    #            names=('name', 'phone', 'idcard'),
    #            header=None,
    #            raise_failed_exception=True)
