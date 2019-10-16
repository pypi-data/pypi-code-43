import json
from json.decoder import JSONDecodeError
from typing import Dict
from typing import Optional, Tuple, Union, List, Any
from urllib.parse import urlencode

import pandas as pd
import requests
from bs4 import BeautifulSoup
from nezha.errors import RequestFailed
from nezha import udict
from nezha.file import File
from nezha.uexcel import Excel
from nezha.upandas import DataFrame


class HuaDaoBase:
    """
    华道返回 xml
    """
    url_access_token = 'http://opensdk.emay.cn:9080/HD_GetAccess_Token.asmx/GetACCESS_TOKEN'

    def __init__(self, token: str):
        self.token: str = token
        self.full_url: str = ''
        self.biz_data: Dict = dict()
        self.response: Dict = dict()

    @classmethod
    def get_token(cls, AppID: str, AppSecret: str, Key: str) -> str:
        full_url = '?'.join((cls.url_access_token, urlencode({
            'AppID': AppID,
            'AppSecret': AppSecret,
            'Key': Key
        })))
        r = requests.get(full_url)
        return r.text

    @staticmethod
    def generate_full_url(url: str, biz_data: Dict[str, str]) -> str:
        """
        you can get full_url by this function return
        :param url: base url
        :param biz_data:
        :return:
        """
        return '?'.join((url, urlencode(biz_data)))

    def set_full_url(self, url: str, biz_data: Dict[str, str]) -> 'HuaDaoBase':
        self.full_url = self.generate_full_url(url, biz_data)
        return self

    def request(self, full_url: str = '') -> Dict[str, str]:
        full_url = full_url or self.full_url
        print(f'full_url {full_url}')
        r = requests.get(full_url)
        if r.ok:
            try:
                bs = BeautifulSoup(r.text, features='html.parser')
                self.response = json.loads(bs.text)
                return self.response
            except JSONDecodeError as e:
                raise TypeError(f'JSONDecodeError, raw resp {r.text}')
            except Exception as e:
                raise SystemError(f'raw resp1 {r.text}')
        else:
            raise ValueError(f'raw resp2 {r.text}')

    def is_succeed(self) -> bool:
        return True


class BankFiveElements(HuaDaoBase):
    url = 'http://opensdk.emay.cn:9099/SF_YZ_API/SFService.asmx/Get_EMW_GetBank_Card_Five_RZ'
    default_part: Dict[Any, Any] = dict()
    df_default_header = ('NAME',
                         'IDCARDCODE',
                         'PHONE',
                         'CARDNO',
                         'ACCOUNT_TYPE',
                         'CODE',
                         'RESULT',
                         'RESULTDESC')
    example = {"CODE": "200", "NAME": "朱**", "IDCARDCODE": "411522****08247578",
               "CARDNO": "623185**496628", "PHONE": "1551**436",
               "RESULT": "2", "RESULTDESC": "认证信息不匹配"}

    def set_biz_data(self,
                     name: str = '',
                     idcard: str = '',
                     cardNo: str = '',
                     phone: str = '',
                     bankAccountType: str = '') -> 'BankFiveElements':
        self.biz_data = udict.Dict.filter(locals())
        self.biz_data['ACCESS_TOKEN'] = self.token
        return self

    def result_as_df(self) -> pd.DataFrame:
        copied = self.response.copy()
        copied['ACCOUNT_TYPE'] = self.biz_data['bankAccountType']
        return DataFrame(copied)


def batch_test(input: str,
               output_file: str,
               names: Optional[Tuple[str, ...]] = ('name', 'idcard', 'phone', 'bankcard', 'account_type'),
               columns: Tuple[str, ...] = BankFiveElements.df_default_header,
               raise_failed_exception: bool = False,
               error_log: Optional[str] = None,
               header: Union[int, List[int], None] = 0,
               token: str = '',
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
    guard_ins = BankFiveElements(token)
    for _, series in excel_ins.dataframe.iterrows():
        name = series['name']
        phone = series['phone']
        idcard = series['idcard']
        bankcard = series['bankcard']
        account_type = series['account_type']
        guard_result = guard_ins.set_biz_data(name=name,
                                              idcard=idcard,
                                              cardNo=bankcard,
                                              phone=phone,
                                              bankAccountType=account_type). \
            set_full_url(guard_ins.url, guard_ins.biz_data).request()
        if not guard_ins.is_succeed():
            if raise_failed_exception:
                raise RequestFailed(f'{guard_result}')
            print('error ins_result  ----> ', guard_result)
            with open(error_log, mode='a') as f:
                print(f"param is idcard={series['idcard']} "
                      f"name={series['name']} phone={series['phone']} bankcard={bankcard}")
                f.write(f"{series['idcard']},{series['name']},{series['phone']}\n")
        # guard_ins.response = guard_ins.example
        print(guard_ins.response)
        guard_result = guard_ins.result_as_df()
        print(guard_result)
        result_df = result_df.append(guard_result)
        print(f'{name} {phone} {idcard} result_df', result_df)
        # break
    result_df.to_excel(output_file, columns=columns, index=False)


if __name__ == '__main__':
    from gitignore import HUADAO_ACCOUNT

    # 姓名电话身份证银行卡
    file = '/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/batch_test/batch_huadao/bankcard5eles.xlsx'
    output = '/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/bankcard5eles_result.xlsx'
    # 姓名	身份证号	银行卡号	手机号	账户类型
    # batch_test(file,
    #            output,
    #            names=('name', 'idcard', 'bankcard', 'phone', 'account_type'),
    #            raise_failed_exception=True,
    #            token=HUADAO_TOKEN)
    # 申请 token
    s = HuaDaoBase.get_token(HUADAO_ACCOUNT['AppID'], HUADAO_ACCOUNT['AppSecret'], HUADAO_ACCOUNT['Key'])
    print(s)
