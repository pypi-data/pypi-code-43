"""
Различные вспомогательные функции для ввода данных через STDIN.

DRY - Don't repeat yourself!
"""

from datetime import datetime


__all__ = (
    'user_input', 'input_int', 'input_float', 'confirm',
    'multi_line_input', 'input_datetime', 'input_date'
)


def user_input(msg='Введите значение', default=None, value_callback=None,
               trim_spaces=True, show_default=True, required=False):
    """
    Запрашивает данные от пользователя и возвращает ввод.

    Arguments:
        msg (str): строка приглашения.
        default: значение, которое будет использовано в случае пустого ввода.
        value_callback (callable): функция обратного вызова для обработки введенного значения.
        trim_spaces (bool): удалять пробельные символы в начале и в конце строки.
        show_default (bool): отобразить значение по-умолчанию в строке приглашении ввода.
        required (bool): обязательное для ввода.
    """
    if show_default and default is not None:
        msg += f' [{default}]'

    if default is not None:
        # Если есть значение по-умолчанию, то либо будет ввод, либо оно возвращается.
        # Аргумент теяет свой смысл.
        required = False

    while 1:
        value = input(f'{msg}: ')

        if trim_spaces:
            value = value.strip()

        if value:
            if value_callback is None:
                return value

            try:
                return value_callback(value)
            except ValueError as e:
                print(e)
        else:
            if not required:
                return default

            print('Требуется ввести значение')


def input_int(msg='Введите число', default=None, required=False):
    """Запрашивает целое число от пользователя и возвращает его."""
    return user_input(msg, default, int, required=required)


def input_bin(msg='Введите число', default=None, required=False):
    """Запрашивает целое число в двоичной СС от пользователя и возвращает его."""
    return user_input(msg, default, lambda v: int(v, 2), required=required)


def input_octet(msg='Введите число', default=None, required=False):
    """Запрашивает целое число в восьмеричной СС от пользователя и возвращает его."""
    return user_input(msg, default, lambda v: int(v, 8), required=required)


def input_hex(msg='Введите число', default=None, required=False):
    """Запрашивает целое число в шестнадцатиричной СС от пользователя и возвращает его."""
    return user_input(msg, default, lambda v: int(v, 16), required=required)


def input_float(msg='Введите число', default=None, required=False):
    """Запрашивает дробное число от пользователя и возвращает его."""
    return user_input(msg, default, float, required=required)


def confirm(msg='Вопрос', default_yes=False, default_no=False, required=False):
    """
    Запрашивает у пользователя подтверждение действия и ожидает ввода Y/Yes или N/No

    Arguments
        msg (str): строка приглашения.
        default_yes (bool): Yes по-умолчанию.
        default_no (bool): No по-умолчанию.

    Returns:
        bool: логическое значение в зависимости от выбранного ответа, либо None.
    """
    def callback(value):
        answers = {
            'y': True,
            'yes': True,
            'n': False,
            'no': False,
        }

        answer = answers.get(value.lower())

        if answer is None:
            valid_values = '/'.join(answers.keys())
            raise ValueError(f'Допустимые значения: {valid_values}')

        return answer

    if default_yes and default_no:
        raise RuntimeError('Оба аргумента default_yes и default_no заданы как True.')

    if default_yes:
        default = True
        msg += ' [Y/n]'
    elif default_no:
        default = False
        msg += ' [y/N]'
    else:
        default = None
        msg += ' [y/n]'

    return user_input(msg, default, callback, show_default=False, required=required)


def multi_line_input(msg='Введите текст', default=None):
    """
    Запрашивает многострочный текст от пользователя и возвращает его.

    Arguments:
        msg (str): строка приглашения.
        default: значение, которое будет использовано в случае пустого ввода.
    """
    print(f'{msg}:')
    print('Ctrl+D/Ctrl+Z (Windows) для завершения ввода')

    if default is not None:
        print('[Оставьте поле пустым, чтобы использовать значение по умолчанию]')

    text = []

    while 1:
        try:
            value = input('> ')

            if not text and not value:
                return default

            text.append(value)
        except EOFError:
            print() # write new line for fix print
            return '\n'.join(text)


def input_datetime(fmt, msg='Введите дату', default=None, required=False):
    """
    Запрашивает дату и время от пользователя через STDIN в указанном формате и возвращает ее.

    Arguments:
        fmt (str): формат даты/времени, см. datetime.strftime()
        msg (str): строка приглашения.
        default: значение, которое будет использовано в случае пустого ввода.
    """
    if default is not None:
        default = default.strftime(fmt)

    return user_input(msg, default, lambda value: datetime.strptime(value, fmt), required=required)


def input_date(fmt, msg='Введите дату', default=None, required=False):
    """
    Запрашивает дату от пользователя через STDIN в указанном формате и возвращает ее.
    """
    value = input_datetime(fmt, msg, default, required=required)

    if value is None:
        return value

    return value.date()


if __name__ == '__main__':
    print(user_input('', required=True))
    # print(confirm(default_yes=True))
    #
    # print(type(input_int()))
    #
    # fmt = '%d/%m/%Y'
    # print(input_date(fmt))
    #
    # value = multi_line_input(default='Description')
    # print(value)
    #
    # started = input_datetime(fmt, default=datetime.now())
    # print(started)
    #
    # planned = input_datetime(fmt, 'Введите дату в формате день/месяц/год')
    # print(planned)
