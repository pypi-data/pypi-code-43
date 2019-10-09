import xmltodict


def is_none(request):
    return request.args


def is_json(request):
    return request.json


def is_form(request):
    return request.form.to_dict()


def is_args(request):
    return request.args.to_dict()


def is_xml(request):
    xml_str = str(request.data, encoding='utf8')
    target = xmltodict.parse(xml_str, encoding='utf-8')
    return target
