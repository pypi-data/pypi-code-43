from collections import OrderedDict
from typing import Dict, Optional, Tuple, Any

import pandas as pd
from nezha import udict
from nezha.errors import RequestFailed
from nezha.file import Dir
from nezha.file import File
from nezha.uexcel import Excel

from .base import BoolDataBase


class LiabilitiesDetails(BoolDataBase):
    interface_chinese_name = '负债详情'
    service = 'multiple_platforms_loan_v2_0'
    mode = 'mode_multiple_platforms_liabilities_detail'
    default_part = {'name': '',
                    'phone': '',
                    'ident_number': ''
                    }
    df_default_header_dict = OrderedDict({'name': '姓名',
                                          'phone': '手机号',
                                          'ident_number': '身份证号',
                                          'cflenders': '消费金融类机构数',
                                          'd7_lend_number': '近7天负债机构数',
                                          'liabilities_mechanism_number': '负债机构总数',
                                          'loanday': '首次负债距今时长',
                                          'm1_lend_number': '近1个月负债机构数',
                                          'm3_lend_number': '近3个月负债机构数',
                                          'm6_lend_number': '近6个月负债机构数',
                                          'nllenders': '网络贷款类机构数',
                                          'settlement_number': '已结清负债机构数'
                                          })

    @classmethod
    def generate_biz_data(cls, name: str, phone: str, ident_number: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, phone: str, ident_number: str) -> 'LiabilitiesDetails':
        self.biz_data = self.generate_biz_data(name, str(phone), str(ident_number))
        return self

    def result_as_df_partial(self, append_biz_data: bool = True) -> pd.DataFrame:
        return self.result_as_df(self.response.get('resp_data', {}),
                                 self.default_part,
                                 append_biz_data=append_biz_data)


class RepaymentDetail(BoolDataBase):
    interface_chinese_name = '还款详情'
    service = 'multiple_platforms_loan_v2_0'
    mode = 'mode_multiple_platforms_repayment_detail'
    default_part = {'name': '',
                    'phone': '',
                    'ident_number': ''
                    }
    df_default_header_dict = OrderedDict({'name': '姓名',
                                          'phone': "手机",
                                          'ident_number': '身份证',
                                          'd7_repay_fail_cnt': '近7天还款失败次数',
                                          'd7_repay_fail_money': '近7天还款失败金额',
                                          'd7_repay_succ_cnt': '近7天成功还款次数',
                                          'd7_repay_succ_money': '近7天成功还款金额',
                                          'last_repay_day': '最近一次成功还款距今天数',
                                          'm1_repay_fail_cnt': '近1个月还款失败次数',
                                          'm1_repay_fail_money': '近1个月还款失败金额',
                                          'm1_repay_succ_cnt': '近1个月成功还款次数',
                                          'm1_repay_succ_money': '近1个月成功还款金额',
                                          'm3_repay_fail_cnt': '近3个月还款失败次数',
                                          'm3_repay_fail_money': '近3个月还款失败金额',
                                          'm3_repay_succ_cnt': '近3个月成功还款次数',
                                          'm3_repay_succ_money': '近3个月成功还款金额',
                                          'm6_repay_fail_cnt': '近6个月还款失败次数',
                                          'm6_repay_fail_money': '近6个月还款失败金额',
                                          'm6_repay_succ_cnt': '近6个月成功还款次数',
                                          'm6_repay_succ_money': '近6个月成功还款金额'
                                          })

    @classmethod
    def generate_biz_data(cls, name: str, phone: str, ident_number: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, phone: str, ident_number: str) -> 'RepaymentDetail':
        # phone not str, parameter error
        self.biz_data = self.generate_biz_data(name, str(phone), str(ident_number))
        return self

    def result_as_df_partial(self, append_biz_data: bool = True) -> pd.DataFrame:
        return self.result_as_df(self.response.get('resp_data', {}),
                                 self.default_part,
                                 append_biz_data=append_biz_data)


class OverdueDetail(BoolDataBase):
    interface_chinese_name = '逾期详情'
    service = 'multiple_platforms_loan_v2_0'
    mode = 'mode_multiple_platforms_overdue_detail'
    default_part = {'name': '',
                    'phone': '',
                    'ident_number': ''
                    }
    df_default_header_dict = OrderedDict({'name': '姓名',
                                          'phone': '手机',
                                          'ident_number': '身份证',
                                          'counts': '逾期机构数',
                                          'is_overdue': '是否逾期',
                                          'overdue_money': '逾期金额',
                                          'settlement': '是否存在逾期未结清'
                                          })

    @classmethod
    def generate_biz_data(cls, name: str, phone: str, ident_number: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, phone: str, ident_number: str) -> 'OverdueDetail':
        self.biz_data = self.generate_biz_data(name, str(phone), str(ident_number))
        return self

    def result_as_df_partial(self, append_biz_data: bool = True) -> pd.DataFrame:
        return self.result_as_df(self.response.get('resp_data', {}),
                                 self.default_part,
                                 append_biz_data=append_biz_data)


class ApplyDetail(BoolDataBase):
    interface_chinese_name = '申请详情'
    service = 'multiple_platforms_loan_v2_0'
    mode = 'mode_multiple_platforms_apply_detail'
    default_part = {'name': '',
                    'phone': '',
                    'ident_number': ''
                    }
    df_default_header_dict = OrderedDict({'name': '姓名',
                                          'phone': '手机',
                                          'ident_number': '身份证',
                                          'apply_mechanism_number': '历史查询调用平台数量',
                                          'd7_apply_times': '近7天查询调用次数',
                                          'm12_apply_times': '近12个月查询调用次数',
                                          'm1_apply_times': '近1个月查询调用次数',
                                          'm3_apply_times': '近3个月查询调用次数',
                                          'm6_apply_times': '近6个月查询调用次数'
                                          })

    @classmethod
    def generate_biz_data(cls, name: str, phone: str, ident_number: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, phone: str, ident_number: str) -> 'ApplyDetail':
        self.biz_data = self.generate_biz_data(name, str(phone), str(ident_number))
        return self

    def result_as_df_partial(self, append_biz_data: bool = True) -> pd.DataFrame:
        return self.result_as_df(self.response.get('resp_data', {}),
                                 self.default_part,
                                 append_biz_data=append_biz_data)


class LoanDetails(BoolDataBase):
    interface_chinese_name = '借款接口合并'
    service = 'multiple_platforms_loan_v2_0'
    mode = 'mode_multiple_platforms_loan_details'
    default_part = {'name': '',
                    'phone': '',
                    'ident_number': ''
                    }

    @classmethod
    def generate_biz_data(cls, name: str, phone: str, ident_number: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, phone: str, ident_number: str) -> 'LoanDetails':
        self.biz_data = self.generate_biz_data(name, str(phone), str(ident_number))
        return self

    def result_as_df_partial(self, append_biz_data: bool = True) -> pd.DataFrame:
        return self.result_as_df(self.response.get('resp_data', {}),
                                 self.default_part,
                                 append_biz_data=append_biz_data)


def batch_test_apply_detail(input: str,
                            input_is_str: bool,
                            account: Dict[str, str],
                            output_file: str,
                            names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                            columns: Optional[OrderedDict] = None,
                            raise_failed_exception: bool = False,
                            error_log: Optional[str] = '',
                            ) -> None:
    """

    :param input: excel file
    :param account: booldata account
    :param output_file: xlsx file that saving booldata personal law result
    :param names: input excel file header, you can adjust the sequence
    :param columns: output_file columns header
    :return: None
    """
    column = columns or ApplyDetail.df_default_header_dict
    error_log = error_log or File.join_path(File(input).dirname, '.'.join((File(input).pure_name, 'error_log')))
    if input_is_str:
        print('batch_test_apply_detail excel_ins', '*' * 10, input, names, '*' * 10)
        excel_ins: pd.DataFrame = Excel.prepare_file(input).read(names=names)
        print('batch_test_apply_detail excel_ins', '*' * 10, excel_ins.dataframe.to_string(), '*' * 10)
    else:
        excel_ins = Excel(input).read(names=names).dataframe if isinstance(input, str) else input
    result_df = pd.DataFrame()
    guard_ins = ApplyDetail(account['rsa_prv_key'], account['aes_key'], account['company_uuid'])
    for _, series in excel_ins.dataframe.iterrows():
        name = series['name']
        phone = series['phone']
        idcard = series['idcard']
        guard_result = guard_ins.set_biz_data(name, phone, idcard).request()
        if guard_ins.is_incoming_data_error():
            raise ImportError(f'response {guard_ins.response} series {series.values}')
        if not guard_ins.is_succeed():
            if raise_failed_exception:
                raise RequestFailed(f'{guard_result}')
            with open(error_log, mode='a') as f:
                print(f"param is {series['idcard']} {series['name']} {series['phone']}")
                f.write(f"{series['idcard']},{series['name']},{series['phone']}\n")
        guard_result_df: pd.DataFrame = guard_ins.result_as_df_partial()
        guard_result_df.rename(columns=column, inplace=True)
        result_df = result_df.append(guard_result_df)
        # break
    print('batch_test_apply_detail', '->', result_df.to_string(), output_file, column, '<-')
    result_df.to_excel(output_file, columns=column.values(), index=False)


def batch_test_overdue_detail(input: str,
                              input_is_str: bool,
                              account: Dict[str, str],
                              output_file: str,
                              names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                              columns: Optional[OrderedDict] = None,
                              raise_failed_exception: bool = False,
                              error_log: Optional[str] = None,
                              ) -> None:
    """

    :param input: excel file
    :param account: booldata account
    :param output_file: xlsx file that saving booldata personal law result
    :param names: input excel file header, you can adjust the sequence
    :param columns: output_file columns header
    :return: None
    """
    columns = columns or OverdueDetail.df_default_header_dict
    error_log = error_log or File.join_path(File(input).dirname, '.'.join((File(input).pure_name, 'error_log')))
    if input_is_str:
        print('batch_test_apply_detail excel_ins', '*' * 10, input, names, '*' * 10)
        excel_ins: pd.DataFrame = Excel.prepare_file(input).read(names=names, skiprows=0)
        print('batch_test_apply_detail excel_ins', '*' * 10, excel_ins.dataframe.to_string(), '*' * 10)
    else:
        excel_ins = Excel(input).read(names=names).dataframe if isinstance(input, str) else input
    result_df = pd.DataFrame()
    guard_ins = OverdueDetail(account['rsa_prv_key'], account['aes_key'], account['company_uuid'])
    for _, series in excel_ins.dataframe.iterrows():
        name = series['name']
        phone = series['phone']
        idcard = series['idcard']
        guard_result = guard_ins.set_biz_data(name, phone, idcard).request()
        if guard_ins.is_incoming_data_error():
            raise ImportError(f'response {guard_ins.response} series {series.values}')
        if not guard_ins.is_succeed():
            if raise_failed_exception:
                raise RequestFailed(f'{guard_result}')
            with open(error_log, mode='a') as f:
                print(f"param is {series['idcard']} {series['name']} {series['phone']}")
                f.write(f"{series['idcard']},{series['name']},{series['phone']}\n")
        guard_result_df: pd.DataFrame = guard_ins.result_as_df_partial()
        guard_result_df.rename(columns=columns, inplace=True)
        result_df = result_df.append(guard_result_df)
        # break
    result_df.to_excel(output_file, columns=columns.values(), index=False)


def batch_test_repayment_detail(input: str,
                                input_is_str: bool,
                                account: Dict[str, str],
                                output_file: str,
                                names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                                columns: Optional[OrderedDict] = None,
                                raise_failed_exception: bool = False,
                                error_log: Optional[str] = None,
                                ) -> None:
    """

    :param input: excel file
    :param account: booldata account
    :param output_file: xlsx file that saving booldata personal law result
    :param names: input excel file header, you can adjust the sequence
    :param columns: output_file columns header
    :return: None
    """
    columns = columns or RepaymentDetail.df_default_header_dict
    error_log = error_log or File.join_path(File(input).dirname, '.'.join((File(input).pure_name, 'error_log')))
    if input_is_str:
        print('batch_test_apply_detail excel_ins', '*' * 10, input, names, '*' * 10)
        excel_ins: pd.DataFrame = Excel.prepare_file(input).read(names=names, skiprows=0)
        print('batch_test_apply_detail excel_ins', '*' * 10, excel_ins.dataframe.to_string(), '*' * 10)
    else:
        excel_ins = Excel(input).read(names=names).dataframe if isinstance(input, str) else input
    result_df = pd.DataFrame()
    guard_ins = RepaymentDetail(account['rsa_prv_key'], account['aes_key'], account['company_uuid'])
    for _, series in excel_ins.dataframe.iterrows():
        name = series['name']
        phone = series['phone']
        idcard = series['idcard']
        guard_result = guard_ins.set_biz_data(name, phone, idcard).request()
        if not guard_ins.is_succeed():
            if guard_ins.is_incoming_data_error():
                raise ImportError(f'response {guard_ins.response} series {series.values}')
            if raise_failed_exception:
                raise RequestFailed(f'{guard_result}')
            with open(error_log, mode='a') as f:
                print(f"param is {series['idcard']} {series['name']} {series['phone']}")
                f.write(f"{series['idcard']},{series['name']},{series['phone']}\n")
        guard_result_df: pd.DataFrame = guard_ins.result_as_df_partial()
        guard_result_df.rename(columns=columns, inplace=True)
        result_df = result_df.append(guard_result_df)
        # break
    result_df.to_excel(output_file, columns=columns.values(), index=False)


def batch_test_liabilities_detail(input: str,
                                  input_is_str: bool,
                                  account: Dict[str, str],
                                  output_file: str,
                                  names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                                  columns: Optional[OrderedDict] = None,
                                  raise_failed_exception: bool = False,
                                  error_log: Optional[str] = None,
                                  ) -> None:
    """

    :param input: excel file
    :param account: booldata account
    :param output_file: xlsx file that saving booldata personal law result
    :param names: input excel file header, you can adjust the sequence
    :param columns: output_file columns header
    :return: None
    """
    columns = columns or LiabilitiesDetails.df_default_header_dict
    error_log = error_log or File.join_path(File(input).dirname, '.'.join((File(input).pure_name, 'error_log')))
    # it's support to raw string and file.
    if input_is_str:
        print('batch_test_apply_detail excel_ins', '*' * 10, input, names, '*' * 10)
        excel_ins: pd.DataFrame = Excel.prepare_file(input).read(names=names, skiprows=0)
        print('batch_test_apply_detail excel_ins', '*' * 10, excel_ins.dataframe.to_string(), '*' * 10)
    else:
        excel_ins = Excel(input).read(names=names).dataframe if isinstance(input, str) else input
    result_df = pd.DataFrame()
    guard_ins = LiabilitiesDetails(account['rsa_prv_key'], account['aes_key'], account['company_uuid'])
    for _, series in excel_ins.dataframe.iterrows():
        name = series['name']
        phone = series['phone']
        idcard = series['idcard']
        guard_result = guard_ins.set_biz_data(name, phone, idcard).request()
        if not guard_ins.is_succeed():
            if guard_ins.is_incoming_data_error():
                raise ImportError(f'response {guard_ins.response} series {series.values}')
            if raise_failed_exception:
                raise RequestFailed(f'{guard_result}')
            with open(error_log, mode='a') as f:
                print(f"param is {series['idcard']} {series['name']} {series['phone']}")
                f.write(f"{series['idcard']},{series['name']},{series['phone']}\n")
        guard_result_df: pd.DataFrame = guard_ins.result_as_df_partial()
        guard_result_df.rename(columns=columns, inplace=True)
        result_df = result_df.append(guard_result_df)
        # break
    result_df.to_excel(output_file, columns=columns.values(), index=False)


def batch_test_used_web(input: str,
                        input_is_str: bool,
                        account: Dict[str, str],
                        output_dir: str,
                        names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone'),
                        raise_failed_exception: bool = True,
                        error_log: Optional[str] = None,
                        ) -> None:
    dir = Dir(output_dir)
    dir.mkdir()
    if not dir.is_dir():
        raise ValueError(f'output_dir {output_dir} must be dir')
    output_liabilities_detail = File.join_path(output_dir, LiabilitiesDetails.interface_chinese_name + '.xlsx')
    batch_test_liabilities_detail(input,
                                  input_is_str,
                                  account,
                                  output_liabilities_detail,
                                  names=names,
                                  raise_failed_exception=raise_failed_exception,
                                  error_log=error_log)
    output_repayment_detail = File.join_path(output_dir, RepaymentDetail.interface_chinese_name + '.xlsx')
    batch_test_repayment_detail(input,
                                input_is_str,
                                account,
                                output_repayment_detail,
                                names=names,
                                raise_failed_exception=raise_failed_exception,
                                error_log=error_log)
    output_dir_overdue_detail = File.join_path(output_dir, OverdueDetail.interface_chinese_name + '.xlsx')
    batch_test_overdue_detail(input,
                              input_is_str,
                              account,
                              output_dir_overdue_detail,
                              names=names,
                              raise_failed_exception=raise_failed_exception,
                              error_log=error_log)
    output_dir_apply_detail = File.join_path(output_dir, ApplyDetail.interface_chinese_name + '.xlsx')
    batch_test_apply_detail(input,
                            input_is_str,
                            account,
                            output_dir_apply_detail,
                            names=names,
                            raise_failed_exception=raise_failed_exception,
                            error_log=error_log)
    dir.zip()
