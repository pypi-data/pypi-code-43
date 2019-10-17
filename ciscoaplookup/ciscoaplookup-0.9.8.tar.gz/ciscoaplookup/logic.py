from xlrd import open_workbook
from xlrd.sheet import Sheet
from xlrd.book import Book
from xlrd.biffh import XLRDError
import requests

"""
This module reads a spreadsheet from cisco.com, which is what is houses the data being used on:
https://www.cisco.com/c/dam/assets/prod/wireless/wireless-compliance-tool/index.html
This page is basically javascript, reading data from the spreadsheet, and then offering it in an interactive web form.
This is all nice and fine, but in certain cases it would be neat if you could automate which specific AP model to buy,
given the country.
"""
compliance_url = 'https://www.cisco.com/c/dam/assets/prod/wireless/wireless-compliance-tool/ComplianceStatus.xls'
platforms = {'Controller-based': (1, 3), 'Standalone': (0, 1), 'Outdoor & Industrial': (1, 2), 'Universal': (0, 1)}
book = None
models_by_platform = None


def parse_row(row, cols, sheet):
    """
    parse a row into a dict
    :param int row: row index
    :param dict cols: dict of header, column index
    :param Sheet sheet: sheet to parse data from
    :return: dict of values key'ed by their column name
    :rtype: dict[str, str]
    """
    vals = {}
    for header, col in cols.items():
        cell = sheet.cell(row, col)
        vals[header] = cell.value
    return vals


def get_book():
    """
    Lazily fetch the spreadsheet, fresh from cisco.com
    :return:
    :rtype: Book
    """
    global book
    if not book:
        xls_data = requests.get(compliance_url, allow_redirects=True).content
        book = open_workbook(file_contents=xls_data, on_demand=True)
    return book


def get_models_by_platform():
    """
    Retrieve all models, arranged as a dict of platforms, each having a list of models
    :return:
    :rtype: dict[str, list]
    """
    global models_by_platform
    global platforms
    if models_by_platform:
        return models_by_platform
    models_by_platform = {}
    for p, indexes in platforms.items():
        models_by_platform[p] = set()
        sheet = get_platform_sheet(p)
        start_col = indexes[1]+1
        try:
            for col in range(start_col, 30):
                txt = sheet.cell(0, col).value
                if txt.find('-'):
                    models_by_platform[p].add(txt.upper())
                else:
                    break
        except IndexError:
            pass
    return models_by_platform


def get_models():
    """
    Get all models in a list
    :return:
    :rtype: list[str]
    """
    models = set()
    for platform, platform_models in get_models_by_platform().items():
        for model in platform_models:
            models.add(model)
    return list(models)


def get_platform_sheet(platform):
    """
    :param str platform:
    :rtype: Sheet
    """
    try:
        sheet = get_book().sheet_by_name(platform)
    except XLRDError as sheet_error:
        if '&' not in platform:
            raise sheet_error
        sheet = get_book().sheet_by_name(platform.replace('&', 'and'))
    return sheet


def get_domain_for(model, country=None):
    """
    Get all valid domains for a given model, in a particular country.
    :param str model:
    :param str country:
    :return:
    """
    valid_domains = set()
    found_country = False
    for platform in get_platform_for(model):
        sheet = get_platform_sheet(platform)
        h = {'Country': platforms[platform][0], 'Regulatory Domain': platforms[platform][1]}
        for header, col in h.items():
            if header != sheet.cell(0, col).value:
                raise ValueError('Found unexpected header at 0,{}: {} vs {}'.format(
                    col, sheet.cell(0, col).value, header))
        for col in range(platforms[platform][1]+1, 30):  # models start just after regulatory domain column
            try:
                if sheet.cell(0, col).value.upper() == model.upper():
                    h[model] = col
                    break
            except IndexError:
                raise ValueError('Unable to find the model {} in the {} platform?'.format(model, platform))
        for row_no in range(1, sheet.nrows):
            row = parse_row(row_no, h, sheet)
            if not row: continue
            if not country or row['Country'].lower() == country.lower():
                found_country = True
                if row[model] == 'x':
                    valid_domains.add(row['Regulatory Domain'])

    if valid_domains:
        return list(valid_domains)
    elif found_country:
        raise ValueError('Found {} for {} - but no active regulatory domains?'.format(model, country))
    else:
        raise ValueError('Couldn\'t find any country matching {}'.format(country))


def get_country_models(model):
    """
    Get all valid domain-specific models for a given model.
    :param str model:
    :return:
    """
    domains = get_domain_for(model, country=None)
    return ['{}{}-K9'.format(model, domain) for domain in domains]


def get_models_for(model, country):
    """
    Get precise model name for a model and country
    :param str model:
    :param str country:
    :return:
    :rtype: list[str]
    """

    domains = get_domain_for(model, country)
    if not domains:
        raise ValueError('Unable to find any valid regulatory domains for {} in {}'.format(model, country))
    return ['{}{}-K9'.format(model.upper(), dom) for dom in domains]


def get_platform_for(model):
    """
    Fetch platform and indexes for respectively country and regulatory domain as a tuple
    :param model:
    :return:
    :rtype: (str, int, int)
    """
    global platforms
    models = get_models_by_platform()
    model_platforms = []
    for platform, platform_models in models.items():
        if model in platform_models:
            model_platforms.append(platform)
    if not model_platforms:
        raise ValueError('Couldn\'t find the model {}'.format(model))
    return model_platforms
