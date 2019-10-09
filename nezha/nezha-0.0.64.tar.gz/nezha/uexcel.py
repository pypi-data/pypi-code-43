import io
from typing import Dict, Any, Union, Optional, List, Tuple
from typing import TextIO
from warnings import warn

import pandas as pd
from nezha.file import File
from nezha.ustring import clean_str
from pandas import DataFrame
from pandas import Series


def read(file: Union[str, TextIO, io.StringIO],
         names: Optional[Tuple[str, ...]] = None,
         clean_item: bool = True,
         remove_chinese_comma: bool = True,
         skiprows: Union[int, Tuple[int, ...], None] = None,
         header: Union[int, List[int], None] = 0) -> DataFrame:
    """
    read file from xlsx or csv and return pd.DataFrame
    :param file:
    :param names: specified pd.DataFrame header
    :param clean_item: remove invisible char
    :param remove_chinese_comma: not work in xlsx, is suit for csv.
    :header
    指定行数用来作为列名，数据开始行数。
    如果文件中没有列名，则默认为0，否则设置为None。
    如果明确设定header=0 就会替换掉原来存在列名。
    header参数可以是一个list例如：[0,1,3]，这个list表示将文件中的这些行作为列标题（意味着每一列有多个标题），
    介于中间的行将被忽略掉（例如本例中的2；本例中的数据1,2,4行将被作为多级标题出现，第3行数据将被丢弃，dataframe的数据从第5行开始。）。
    :return:
    """
    if isinstance(file, str):
        if file.endswith('xlsx'):
            print(file, names, skiprows, header)
            df = pd.read_excel(file, names=names, skiprows=skiprows, header=header)
        else:
            if not file.endswith('csv'):
                warn(f"{file} treated as csv file")
            if remove_chinese_comma:
                file = File(file).remove_chinese_comma()
            if isinstance(file, io.StringIO):
                df = pd.read_csv(file, names=names, skiprows=skiprows, header=header)
                file.close()
            elif isinstance(file, str):
                df = pd.read_csv(file, names=names, encoding=File(file).encoding, skiprows=skiprows, header=header)
            else:
                raise NotImplementedError(f'file type {type(file)}')
        if not clean_item:
            return df
        frame = []
        for _, series in df.iterrows():
            new_series = {clean_str(k): clean_str(v, striped='"') for k, v in series.iteritems()}
            frame.append(new_series)
        return pd.DataFrame(frame)
    elif isinstance(file, io.StringIO):
        if remove_chinese_comma:
            file = File(file).remove_chinese_comma()
        df = pd.read_csv(file, names=names, skiprows=skiprows, header=header)
        if isinstance(file, io.StringIO):
            file.close()
        return df
    else:
        raise NotImplementedError(f'file type {type(file)}')


def to_excel(df: pd.DataFrame,
             output_name: str,
             index: bool = False,
             columns: Optional[Tuple[str, ...]] = None) -> None:
    df.to_excel(output_name, index=index, columns=columns)


def read_str_csv(s: str, sep: str = '\r\n') -> TextIO:
    """

    :param s:
    example: 'name,phone,idcard\r\n\r\n张**,1536**,14273219***\r\n\r\n韩**,1521**7881,370303**6110320'
    :return: stringIO. csv
    """
    invalid_lines = ('',)
    lines = (line.strip() + '\n' for line in s.split(sep) if line not in invalid_lines)
    io_text = io.StringIO()
    # even call writelines, \n must be added too. It's strange ...
    io_text.writelines(lines)
    io_text.seek(0)
    return io_text


class Excel:

    def __init__(self, file: Union[str, TextIO]):
        """
        as pandas doc, the file is io file-like object.
         you can refer pd.read_html()/pd.read_excel() ... first parameter
        :param file:
        """
        self.file: Union[str, TextIO] = file
        self.dataframe: DataFrame = DataFrame()

    def read(self, names: Optional[Tuple[str, ...]] = None, clean_item: bool = True,
             remove_chinese_comma: bool = True, skiprows: Union[int, Tuple[int, ...], None] = None,
             header: Union[int, List[int], None] = 0) -> 'Excel':
        """

        :param names: if name is not None and the file first row is column_name, skiprows should be 0.
            So the first row will be skipped.
        :param clean_item:
        :param remove_chinese_comma:
        :param skiprows: 需要忽略的行数（从文件开始处算起），或需要跳过的行号列表（从0开始)。
        :return:
        """
        self.dataframe = read(self.file, names=names, clean_item=clean_item, remove_chinese_comma=remove_chinese_comma,
                              skiprows=skiprows, header=header)
        return self

    @property
    def header(self) -> List[str]:
        return list(self.dataframe)

    @classmethod
    def prepare_file(cls, s: str, is_csv: bool = True, sep: str = '\r\n') -> 'Excel':
        if not is_csv:
            raise NotImplementedError()
        file = read_str_csv(s, sep=sep)
        return cls(file)

    def to_excel(self, output_name: str, index: bool = False, columns: Optional[Tuple[str, ...]] = None) -> None:
        print('self.dataframe', self.dataframe)
        to_excel(self.dataframe, output_name, index=index, columns=columns)

    def get_row(self, index: Union[str, int]) -> Series:
        return self.dataframe.loc[index]

    def read_html(self) -> 'Excel':
        self.dataframe = pd.read_html(self.file, encoding='utf-8')
        return self


def csv2xlsx(input: str, output: str, names: Optional[Tuple[str, ...]] = None) -> None:
    """
    usage:
        turn pure csv to xlsx because of scientific notation.
    :param input:
    :param output:
    :param names:
    :return:
    """
    Excel(input).read(names=names).to_excel(output, columns=names)


class Json2Excel:
    """
    template.xlsx content:
    + first row is chinese header
    + second row is json fields

    transform json to excel as the template.xlsx provided
    the transformation rule is:
    + model 'a' matches to json field "a" value
    + model 'a.b' matches to "b" in json field "a" values
    """

    def __init__(self, template_path: str):
        self.template_path: str = template_path
        self._template: Dict = dict()
        self._reversed_template: Dict = dict()

    @classmethod
    def get_recursively(cls, param_key: str, adict: Dict[str, Any]) -> Union[Dict[str, Any], str, None]:
        if isinstance(adict, dict):
            for k, v in adict.items():
                if k != param_key:
                    result = cls.get_recursively(param_key, v)
                    if result is not None:
                        return result
                else:
                    return v
        return None

    @classmethod
    def get_recursively_multi_nest(cls, multi_nest_key: str, data: Dict[str, Any]) -> Any:
        """

        :param multi_nest_key: like 'a.b.c'
        :param data:
        :return:
        """
        fields = multi_nest_key.split('.')
        not_contain_dot = 1
        if len(fields) == not_contain_dot:
            return cls.get_recursively(multi_nest_key, data)
        else:
            first_key, left_keys = fields[0], fields[1:]
            result = cls.get_recursively(first_key, data)
            if isinstance(result, dict):
                nest_key = '.'.join(left_keys)
                return cls.get_recursively_multi_nest(nest_key, result)
            else:
                return result

    def _get_result_val(self, key: str, resp_data: dict) -> str:
        result = self.get_recursively_multi_nest(key, resp_data)
        return result

    @property
    def template(self) -> Dict[str, str]:
        """
        read template.xlsx and transfer to dict.
        :return: dict[chinese, english],
        """
        if not self._template:
            self._template = Excel(self.template_path).read(header=0).dataframe.to_dict(orient='records')[0]
        return self._template

    @property
    def reversed_template(self) -> Dict[str, str]:
        """
        reverse template dict[chinese, english] to dict[chinese, english]
        :return: dict(english=[chinese])
        """
        if not self._reversed_template:
            self._reversed_template = {v: k for k, v in self.template.items()}
        return self._reversed_template

    def parse(self, input: Dict[str, Any], output: str = 'dataframe', index: Optional[List[int]] = None) -> Union[
        Dict[str, Any], pd.DataFrame]:
        """
        parse input by self.reversed_template
        call it like that: result = self.parse(input, output='dataframe', index=index)

        :param input: input data
        :param output: output type: dict/pd.DataFrame
        :param index: if output type is pd.DataFrame and dict value is scalar value, need index
        :return:
        """
        collections = {}
        for key_english, key_chinese in self.reversed_template.items():
            val = self.get_recursively_multi_nest(key_english, input)
            collections[key_chinese] = str(val)
        if output == 'dict':
            return collections
        elif output.lower() == 'dataframe':
            return pd.DataFrame(collections, index=index)
        else:
            raise NotImplementedError(f'output {output} is not support')

    @staticmethod
    def to_excel(df: pd.DataFrame, output: str, columns: Optional[Tuple[str, ...]] = None) -> None:
        """

        :param pf: need persist data
        :param output: output file name
        :param columns: specified the columns name in xlsx file
        :return:
        """
        if not output.endswith('xlsx'):
            raise ValueError(f'output {output} must be xlsx file')
        to_excel(df, output, columns=columns)


if __name__ == '__main__':
    # customer summary
    s = '/Users/yutou/Downloads/sqlResult_2619038.csv'
    names = ('start_time', 'end_time', 'name', 'company_balance', 'company_cost')
    w = Excel(s).read(names=names).to_excel(
        '/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/sqlresut_09bill.xlsx',
        columns=names, index=False)
    print(w)
    # supplier detail
    # s = '/Users/yutou/go/src/supplier_bill.csv'
    # w = Excel(s).read().to_excel('/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/supplier_bill_09.xlsx', index=False)
    # print(w)
    # supplier summary
    # s = '/Users/yutou/Downloads/supplier_sample.xlsx'
    # df = Excel(s).read().dataframe
    # df['product_price'] = pd.to_numeric()
    # result = df.to_numeric(df['product_price']).groupby(by=['supplier_name','product_name'], as_index=False)['product_price'].sum()
    # print(result)
