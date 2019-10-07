#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File name: transform
# Author: Oswaldo Cruz Simon
# Email: oswaldo_cs_94@hotmail.com
# Maintainer: Oswaldo Cruz Simon
# Date created: 03/10/19
# Date last modified: 03/10/19
# Project Name: scrapingtools

import json
import re


def clean_price(price, currency='mxn'):
    if currency == 'mxn':
        return float(delete_extra_blanks(price).replace("$", '').replace(',', ''))
    elif currency == 'cop':
        return float(delete_extra_blanks(price).replace("$", '').replace('.', '').replace(',', '.'))
    else:
        raise ValueError


def delete_extra_blanks(phrase):
    return re.sub('\s\s+', ' ', phrase).strip()


def to_key(pharse):
    return delete_extra_blanks(replace_accents(pharse)).replace(',', '').replace(' - ', '-').replace(' ', '_').lower()


def get_json_inside_script_tag(soup, pattern_str):
    try:
        pattern = re.compile(pattern_str)
        script = soup.find("script", text=pattern)
        script_code = script.get_text(strip=True)
        product_json = json.loads(re.search(pattern_str, script_code).group('data'))
        return product_json
    except Exception as e:
        raise e
        return {}


def get_data_inside_script_tag(soup, pattern_str):
    try:
        pattern = re.compile(pattern_str)
        script = soup.find("script", text=pattern)
        script_code = script.get_text(strip=True)
        return re.search(pattern_str, script_code).group('data')
    except Exception as e:
        return None


def replace_accents(phrase):
    return phrase.replace('á', 'a').replace('é', 'e').\
        replace('ñ', 'n').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
