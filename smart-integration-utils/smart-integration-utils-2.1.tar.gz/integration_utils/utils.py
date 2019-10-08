import re
from decimal import Decimal


def get_operations(data):
    if data:
        if "cogs" in data or "crm_net_cost" in data:
            data["first_cost"] = data.pop('cogs') if "cogs" in data else data.pop('crm_net_cost')
        if "revenue" in data or "crm_deal_cost" in data:
            data['transaction_amount'] = data.pop('revenue') if "revenue" in data else data.pop('crm_deal_cost')
        return {field: str(data[field]).replace('{', '').replace('}', '') for field in data if data[field]}
    return {}


def calc(s):
    val = s.group()
    if not val.strip():
        return val
    return "%s" % eval(val.strip(), {'__builtins__': None})


def calculate(s):
    return re.sub(r"([0-9\ \.\+\*\-\/(\)]+)", calc, s)


def replacer(string: str, data: dict) -> str:
    for fname, fvalue in data.items():
        if fname in string:
            string = string.replace(fname, Decimal(fvalue).__str__())
    return string


def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)
