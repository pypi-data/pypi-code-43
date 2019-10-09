import pandas as pd
import re
from numpy import nan
from datetime import datetime

mapping = {'января': '01',
           'февраля': '02',
           'марта': '03',
           'апреля': '04',
           'мая': '05',
           'июня': '06',
           'июля': '07',
           'августа': '08',
           'сентября': '09',
           'октября': '10',
           'ноября': '11',
           'декабря': '12',
           'январь': '01',
           'февраль': '02',
           'март': '03',
           'апрель': '04',
           'май': '05',
           'июнь': '06',
           'июль': '07',
           'август': '08',
           'сентябрь': '09',
           'октябрь': '10',
           'ноябрь': '11',
           'декабрь': '12',
           }


def replacer(match_obj):
    match_str = match_obj.group()
    return match_str[0] + match_str[2]


def regexp_shielding(S):
    slash = '\\'
    for c in S:
        if c in '{([|&^$"\\\'\"':
            S = S.replace(c, slash + c)
    return S


def filtered_string(content, delete_words=None):
    """
    Эта функция делает следующие  преобразования со строкой:
    - Удаляет пробелы по краям строки
    - Удаляет подстроки из списка delete_words
    - Удаляет пробелы подряд в строке, оставляя один
    Реализована с помощью регулярных выражений.

    Parameters
    ----------
    content: (str) - целевая строка
    delete_words: (list of str) - подстроки, которые надо удалить из целевой строки

    Returns
    -------
    (str) - обработанная строка
    """
    if delete_words is None:
        delete_words = []
    if content != nan:
        content = str(content)
        content = content.strip()
        reg_state = ''
        content = re.sub('^(?=\s)|$(?=\s)|' + '|'.join(delete_words), '', content)  # replacing words
        content = re.sub('\s{2,}', ' ', content)  # replacing multiple whitespaces
        content = re.sub('[0-9.,:;\'&$!?@#`~%^*+_={}()[—><\]\"\\\|\-]\s[0-9.,:;\'&$!?@#`~%^*+_={}()[—><\]\"\\\|\-]',
                         replacer, content)  # replacing whitespaces between digits and punctuation signes

    return content


def filtered_string_DEPRECATED(content, delete_words=None):
    """
    Эта функция делает следующие  преобразования со строкой:
    - Удаляет пробелы по краям строки
    - Удаляет подстроки из списка delete_words
    - Удаляет пробелы подряд в строке, оставляя один

    Parameters
    ----------
    content: (str) - целевая строка
    delete_words: (list of str) - подстроки, которые надо удалить из целевой строки

    Returns
    -------
    (str) - обработанная строка
    """

    if delete_words is None:
        delete_words = []
    if content != float('nan'):
        content = str(content)
        if delete_words:
            for word in delete_words:
                content = content.replace(word, '')
        content = content.strip()
        tmp = ''
        i = 0
        while i < len(content):
            if (i < len(content) - 1) and (content[i] + content[i + 1] != '  '):
                tmp += content[i]
            elif i == len(content) - 1:
                tmp += content[i]
            i += 1
        content = tmp
    return content


def to_str(S, filtering=False, delete_words=None):
    """

    Parameters
    ----------
    S (pd.Series) : объект pd.Series, объекты которого нужно перевести в строки
    filtering (boolean) : флаг, который отвечает за проведение фильтрации строк на лишние пробелы и какие-либо подстроки
    delete_words (list of str) : подстроки, которые надо удалить из каждого объекта S (только если filtering=True)

    Returns
    -------
    (pd.Series) : обработанный S
    """

    if delete_words is None:
        delete_words = []
    mS = None
    if isinstance(S, pd.Series):
        if filtering:
            try:
                mS = S.apply(lambda x: filtered_string(x, delete_words=delete_words))
            except Exception as error:
                print('Caught this error, when was trying to convert series object to str: {}'.format(repr(error)))
        else:
            try:
                mS = S.apply(str)
            except Exception as error:
                print('Caught this error, when was trying to convert series object to str: {}'.format(repr(error)))
    else:
        raise Exception('Passed object is not a pd.Series')
    return mS


def isint(s):
    """
    Функция, которая возращает True, если  строка является целым числом, и False в ином случае.
    Parameters
    ----------
    s (str) : строка с целым числом.

    Returns
    -------
    (boolean) True, если  строка является целым числом, и False в ином случае.
    """

    if isinstance(s, str):
        try:
            s = int(s)
            return True
        except:
            return False
    else:
        return False


def to_digit(val):
    """
    Функция, которая возращает превращает строку в int,
    если  получится.
    Иначе - во float. Если в строке не число, то вернется None
    Parameters
    ----------
    s (str) : строка с целым числом.

    Returns
    -------
    (boolean) True, если  строка является целым числом, и False в ином случае.
    """
    if isinstance(val, int):
        digital = int(val)
    elif isinstance(val, float):
        digital = float(val)
    else:
        digital = val
    return digital


def to_date(input_date):
    """

    Parameters
    ----------
    input_date

    Returns
    -------

    """
    '''
    Case 1 (input is string):
        Parameters
        ----------
            input (str) : строка, содержащая дату в одном из следующих форматов:
                • '01.01.2500'
                • '01-01-2050'
                • '01 01 2050'
                • '1 января 2050'
                • 'январь  2050'
        Returns
        -------
            whole_date (datetime.datetime) объект datetime соответсвующей даты.

    Case 2 (input is pd.Series):
        Функция переводит все строковые элементы, содержащие дату в объекты 
        типа datetime
        
        Parameters
        -------
            input (pd.Series) : объект pd.Series со строками, содержашими дату, и которые нужно перевести в объекты 
            типа datetime
        
        Returns
        -------
            (pd.Series) : обработанный input, в котором все строковые элементы преобразованы в объекты datetime
    '''

    def to_date_single(date):
        global mapping
        date = filtered_string(date).lower()
        if date.find(' ') != -1:
            sep = ' '
        elif date.find('-') != -1:
            sep = '-'
        elif date.find('.') != -1:
            sep = '.'
        else:
            sep = 0
            raise Exception(
                'No separator found. Passed string doesnt contain supportable string format.\n{}'.format(date))
        if sep:
            date_tmp = date.split(sep)
            if len(date_tmp) == 3:
                to_do_mapping = False
                for month_name in list(mapping.keys()):
                    if month_name in date:
                        to_do_mapping = True
                if to_do_mapping:
                    date_tmp[1] = mapping[date_tmp[1]]  # месяц словами
            elif len(date_tmp) == 2:
                if not isint(date_tmp[0]):
                    if date_tmp[0].lower() in list(mapping.keys()):
                        date_tmp[0] = mapping[date_tmp[0]]
                        date_tmp = [
                                       '15'] + date_tmp  # так как этот случай описывает дату без конкретного числа,
                        # возьмем середину месяца
            whole_date = '.'.join(date_tmp)
            whole_date = datetime.strptime(whole_date, '%d.%m.%Y').date()
            return whole_date
        else:
            return date

    if isinstance(input_date, str):
        date = input_date
        res = to_date_single(date)
        return res

    elif isinstance(input_date, pd.Series):
        S = input_date
        mS = None
        try:
            mS = S.apply(to_date_single)
        except Exception as error:
            print('Caught this error, when was trying to convert str to datetime: {}'.format(repr(error)))
        return mS
    else:
        raise Exception('Passed object is not string or a pd.Series')
        return input_date


def to_numeric_single(val, delete_words=None, replace_all_non_digits_or_dots=False):
    """
    Преобразует строку с вещественным числом в число типа float. Если указать в списке подстрок для удаления
    точку, то функция выдаст число типа integer.
    Производит удаление из строки всех точек после первой по порядку точки.
    Может удалять указанные подстроки или удалять все не цифры или не точки.

    Parameters
    ----------
    val (string) : строка, содержащая число, которое нужно преобразовать в int или float
    delete_words (list of strings) : список подстрок для удаления из целевой строки
    replace_all_non_digits_or_dots (boolean) : флаг для опции удаления всех не цифр или не точек из строки

    Returns
    -------
    (int или float) : число, полученное из строки.
    """
    if delete_words is None:
        delete_words = []
    val = re.sub('\.{2,}', '.', val)  # замена многоточий на одну точку
    delete_words_string = regexp_shielding('|'.join(delete_words))  # добавление к служебным знакам ($, ...) экрана "\"
    val = re.sub('^(?=\s)|$(?=\s)|' + delete_words_string, '', val)  # убирание подстрок из строки
    if replace_all_non_digits_or_dots:
        val = re.sub('[^\.\d]', '', val)
    if '.' in val:
        val = val[:re.search('\.', val).end()] + re.sub('\.', '', val[re.search('\.',
                                                                                val).end():])  # удаление всех точек из
    # строки после первой точки
    return to_digit(val)


def to_numeric(val, delete_words=[], replace_all_non_digits_or_dots=False):
    """
    Вариант 1 (input is string):
        Parameters
        ----------
            val (str) : строка, которую нужно преобразовать в число
            delete_words (list или str) : список подстрок для удаления из целевой строки
            replace_all_non_digits_or_dots (boolean) : флаг для опции удаления всех не цифр или не точек из строки
        Returns
        -------
            (int или float) : значение, полученное из входной строки

    Вариант 2 (input is pd.Series):
        Parameters
        ----------
            val (pd.Series) : объект pd.Series, содержащий строки, которые нужно преобразовать в числа
            delete_words (list или str) : список подстрок для удаления из каждого строкового объекта
                                          в последовательности val
            replace_all_non_digits_or_dots (boolean) : флаг для опции удаления всех не цифр или не точек из строки
            replace_all_non_digits_or_dots (boolean) : флаг для опции удаления всех не цифр или не точек из строк
        Returns
        -------
            (pd.Series) : объект pd.Series из чисел
    """

    if isinstance(val, str):
        val = to_numeric_single(val, delete_words=delete_words,
                                replace_all_non_digits_or_dots=replace_all_non_digits_or_dots)
    elif isinstance(val, pd.Series):
        val = val.apply(lambda x: to_numeric_single(x, delete_words=delete_words,
                                                    replace_all_non_digits_or_dots=replace_all_non_digits_or_dots))
    else:
        print('Not proper type of input variable (val type  is {type})'.format(type=type(val)))
        val = None

    return val