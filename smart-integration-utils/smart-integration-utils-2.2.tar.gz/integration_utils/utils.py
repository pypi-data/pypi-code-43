import re
from decimal import Decimal


def get_operations(data: dict) -> dict:
    """
    create valid calculation dict
    :param data: dict
    :return: dict
    """
    if data:
        if "cogs" in data or "crm_net_cost" in data:
            data["first_cost"] = data.pop('cogs') if "cogs" in data else data.pop('crm_net_cost')
        if "revenue" in data or "crm_deal_cost" in data:
            data['transaction_amount'] = data.pop('revenue') if "revenue" in data else data.pop('crm_deal_cost')
        return {field: str(data[field]).replace('{', '').replace('}', '') for field in data if data[field]}
    return {}


def calc(s: str) -> str:
    """
    :param s: str (value like ('(1 * 2) / 3'))
    :return: str (result of math operation)
    """
    val = s.group()
    if not val.strip():
        return val
    return "%s" % eval(val.strip(), {'__builtins__': None})


def calculate(s: str) -> str:
    """
    :param s: str
    :return: str
    """
    return re.sub(r"([0-9\ \.\+\*\-\/(\)]+)", calc, s)


def replacer(string: str, data: dict) -> str:
    """
    replace for calculated data
    :param string: str
    :param data: str
    :return: str
    """
    for name, value in data.items():
        if name in string:
            string = string.replace(name, Decimal(value).__str__())
    return string


def remove_tags(text: str) -> str:
    """
    remove html tags from text
    :param text: str
    :return: str
    """
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)
