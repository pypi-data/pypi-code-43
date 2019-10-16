from typing import Any
from typing import Dict, Optional, Tuple, Union, List

import pandas as pd
from nezha.errors import RequestFailed
from nezha import udict
from nezha.file import File
from nezha.uexcel import Excel

from .base import BoolDataBase


class Bankcard5Eles(BoolDataBase):
    service = 'bankcard_five_elements_service'
    mode = 'bankcard_five_elements_mode'

    default_part = [{
        "result_code": '',
        "result_code_desc": ""
    }]

    @classmethod
    def generate_biz_data(cls, name: str, ident_number: str, bankcard: str, phone: str, account_type: str = '1') -> \
            Dict[
                str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str,
                     ident_number: str,
                     bankcard: str,
                     phone: str,
                     account_type: str) -> 'Bankcard5Eles':
        """
        support, Bankcard5Eles().set_biz_data().request()
        :param name:
        :param ident_number:
        :param bankcard:
        :param phone:
        :param account_type:
        :return:
        """
        self.biz_data = self.generate_biz_data(name, ident_number, bankcard, phone, account_type=account_type)
        return self


def batch_test(input: str,
               account: Dict[str, str],
               output_file: str,
               names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone', 'bankcard'),
               columns: Tuple[str, ...] = Bankcard5Eles.df_default_header,
               raise_failed_exception: bool = False,
               error_log: Optional[str] = None,
               header: Union[int, List[int], None] = 0,
               env: str = "prod"
               ) -> None:
    """
    batch test personal law, read from excel -> request personal law -> save result to excel

    :param input: excel file
    :param account: booldata account
    :param output_file: xlsx file that saving booldata personal law result
    :param names: input excel file header, you can adjust the sequence
    :param columns: output_file columns header
    :return: None
    """
    error_log = error_log or File.join_path(File(input).dirname, '.'.join((File(input).pure_name, 'error_log')))
    excel_ins = Excel(input).read(names=names, header=header)
    result_df = pd.DataFrame()
    guard_ins = Bankcard5Eles(account['rsa_prv_key'], account['aes_key'], account['company_uuid'],
                              Bankcard5Eles.urls[env])
    for _, series in excel_ins.dataframe.iterrows():
        name = series['name']
        phone = series['phone']
        idcard = series['idcard']
        bankcard = series['bankcard']
        account_type = series['account_type']
        guard_result = guard_ins.set_biz_data(name, idcard, bankcard, phone, account_type).request()
        if not guard_ins.is_succeed():
            if raise_failed_exception:
                raise RequestFailed(f'{guard_result}')
            print('error ins_result  ----> ', guard_result)
            with open(error_log, mode='a') as f:
                print(f"param is idcard={series['idcard']} "
                      f"name={series['name']} phone={series['phone']} bankcard={bankcard}")
                f.write(f"{series['idcard']},{series['name']},{series['phone']}\n")
        print(guard_ins.response)
        guard_result = guard_ins.result_as_df(guard_ins.response.get('resp_data'), guard_ins.default_part)
        print(guard_result)
        result_df = result_df.append(guard_result)
        print(f'{name} {phone} {idcard} result_df', result_df)
    result_df.to_excel(output_file, columns=columns, index=False)


if __name__ == '__main__':
    from gitignore import BOOLDATA_ACCOUNT

    s = Bankcard5Eles(BOOLDATA_ACCOUNT['rsa_prv_key'],
                      BOOLDATA_ACCOUNT['aes_key'],
                      BOOLDATA_ACCOUNT['company_uuid'],
                      Bankcard5Eles.urls['prod']).set_biz_data('**',
                                                               '**',
                                                               '**',
                                                               '**', '1').request()
