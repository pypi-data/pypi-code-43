import pdb
import numpy as np
import json as js
import sys
import csv
from functools import wraps
import json
import requests
from glom import glom, T
import itertools
import tempfile
import random
import re
from time import sleep
import pkg_resources
from multiprocessing.pool import ThreadPool
from demyst.analytics.report import report
from yattag import Doc
from IPython.display import HTML,display
import ipywidgets as widgets
from datetime import datetime

from demyst.common.config import load_config
from demyst.common.connectors import Connectors, DemystConnectorError
from demyst.common.track import track_function
from demyst.analytics.shiny import progressbar
from demyst.analytics.shiny import generatehandlerbutton
from demyst.analytics.type_guesser import TypeGuesser

import os
import pandas as pd
from pandas.api.types import is_string_dtype

from pandas_schema import Column, Schema
from pandas_schema.validation import MatchesPatternValidation, IsDtypeValidation, InListValidation, CanCallValidation

from urllib.parse import urlparse, urlencode

import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')

non_empty_validation = MatchesPatternValidation(r'.+')
decimal_number_validation = MatchesPatternValidation(r'^[+-]?\d*(\.\d+)?$')

percentage_validation = non_empty_validation & MatchesPatternValidation(r'^\d*(\.\d+)?%?$')
number_validation = non_empty_validation & decimal_number_validation
first_name_validation = non_empty_validation
last_name_validation = non_empty_validation
middle_name_validation = non_empty_validation
city_validation = non_empty_validation
business_name_validation = non_empty_validation
marital_status_validation = non_empty_validation & InListValidation([
        "A", "ANNULLED",
        "D", "DIVORCED",
        "I", "INTERLOCUTORY",
        "L", "LEGALLY SEPARATED",
        "M", "MARRIED",
        "P", "POLYGAMOUS",
        "S", "NEVER MARRIED", "SINGLE",
        "T", "DOMESTIC PARTNER",
        "U", "UNMARRIED",
        "W", "WIDOWED"
        ], case_sensitive=False)
email_address_validation = non_empty_validation & MatchesPatternValidation(r'^[^@]+@[^@]+\.[^@]+$')
ip4_validation = non_empty_validation & MatchesPatternValidation(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
latitude_validation = non_empty_validation & MatchesPatternValidation(r'^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$') # https://jex.im/regulex/#!embed=true&flags=&re=%5E(%5C%2B%7C-)%3F(%3F%3A90(%3F%3A(%3F%3A%5C.0%7B1%2C6%7D)%3F)%7C(%3F%3A%5B0-9%5D%7C%5B1-8%5D%5B0-9%5D)(%3F%3A(%3F%3A%5C.%5B0-9%5D%7B1%2C6%7D)%3F))%24
longitude_validation = non_empty_validation & MatchesPatternValidation(r'^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$') # https://jex.im/regulex/#!cmd=export&flags=&re=%5E(%5C%2B%7C-)%3F(%3F%3A180(%3F%3A(%3F%3A%5C.0%7B1%2C6%7D)%3F)%7C(%3F%3A%5B0-9%5D%7C%5B1-9%5D%5B0-9%5D%7C1%5B0-7%5D%5B0-9%5D)(%3F%3A(%3F%3A%5C.%5B0-9%5D%7B1%2C6%7D)%3F))%24
full_name_validation = non_empty_validation
domain_validation = non_empty_validation & MatchesPatternValidation(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
year_month_validation = non_empty_validation & MatchesPatternValidation(r'^\d{4}-\d{2}$')
year_validation = non_empty_validation & MatchesPatternValidation(r'^\d{4}$')
string_validation = non_empty_validation
country_validation = non_empty_validation & MatchesPatternValidation(r'(?i)^(AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW)$')
us_ein_validation = non_empty_validation & MatchesPatternValidation(r'^\d\d-?\d\d\d\d\d\d\d$')
us_ssn_validation = non_empty_validation & MatchesPatternValidation(r'^\d\d\d-?\d\d-?\d\d\d\d$')
us_ssn4_validation = non_empty_validation & MatchesPatternValidation(r'^\d\d\d\d$')
sic_code_validation = non_empty_validation & MatchesPatternValidation(r'^\d\d\d\d$')
gender_validation = non_empty_validation & MatchesPatternValidation(r'(?i)^m(ale)?$|^f(emale)?$')
post_code_validation = non_empty_validation & MatchesPatternValidation(r'^[0-9A-Z -]{3,}$')
# XXX The following are simply passed through to BKF without any checking:
state_validation = non_empty_validation & InListValidation([
        "AL", "Alabama",
        "AK", "Alaska",
        "AZ", "Arizona",
        "AR", "Arkansas",
        "AE", "Armed Forces in Europe, the Middle East, Africa, and Canada",
        "AA", "Armed Forces in the Americas",
        "AP", "Armed Forces in the Pacific",
        "CA", "California",
        "CO", "Colorado",
        "CT", "Connecticut",
        "DE", "Delaware",
        "DC", "District Of Columbia",
        "FL", "Florida",
        "GA", "Georgia",
        "HI", "Hawaii",
        "ID", "Idaho",
        "IL", "Illinois",
        "IN", "Indiana",
        "IA", "Iowa",
        "KS", "Kansas",
        "KY", "Kentucky",
        "LA", "Louisiana",
        "ME", "Maine",
        "MD", "Maryland",
        "MA", "Massachusetts",
        "MI", "Michigan",
        "MN", "Minnesota",
        "MS", "Mississippi",
        "MO", "Missouri",
        "MT", "Montana",
        "NE", "Nebraska",
        "NV", "Nevada",
        "NH", "New Hampshire",
        "NJ", "New Jersey",
        "NM", "New Mexico",
        "NY", "New York",
        "NC", "North Carolina",
        "ND", "North Dakota",
        "OH", "Ohio",
        "OK", "Oklahoma",
        "OR", "Oregon",
        "PA", "Pennsylvania",
        "PR", "Puerto Rico",
        "RI", "Rhode Island",
        "SC", "South Carolina",
        "SD", "South Dakota",
        "TN", "Tennessee",
        "TX", "Texas",
        "UT", "Utah",
        "VT", "Vermont",
        "VA", "Virginia",
        "WA", "Washington",
        "WV", "West Virginia",
        "WI", "Wisconsin",
        "WY", "Wyoming",
        # Canada
        "09", "Quebec",
        "17", "Saskatchewan",
        "AB", "Alberta",
        "BC", "British Columbia",
        "MB", "Manitoba",
        "NB", "New Brunswick",
        "NL", "Newfoundland and Labrador",
        "NS", "Nova Scotia",
        "NT", "Northwest Territories",
        "NU", "Nunavut",
        "ON", "Ontario",
        "PE", "Prince Edward Island",
        "YT", "Yukon",
        # Mexico
        "AGU", "Aguascalientes",
        "BCN", "Baja California",
        "BCS", "Baja California Sur",
        "CAM", "Campeche",
        "CHH", "Chihuahua",
        "CHP", "Chiapas",
        "CMX", "Mexican Federal District",
        "COA", "Coahuila",
        "COL", "Colima",
        "DUR", "Durango",
        "GRO", "Guerrero",
        "GUA", "Guanajuato",
        "HID", "Hidalgo",
        "JAL", "Jalisco",
        "MEX", "México",
        "MIC", "Michoacán",
        "MOR", "Morelos",
        "NAY", "Nayarit",
        "NLE", "Nuevo León",
        "OAX", "Oaxaca",
        "PUE", "Puebla",
        "QUE", "Querétaro",
        "ROO", "Quintana Roo",
        "SIN", "Sinaloa",
        "SLP", "San Luis Potosí",
        "SON", "Sonora",
        "TAB", "Tabasco",
        "TAM", "Tamaulipas",
        "TLA", "Tlaxcala",
        "VER", "Veracruz",
        "YUC", "Yucatán",
        "ZAC", "Zacatecas"
        ], case_sensitive=False)
street_validation = non_empty_validation
blob_validation = non_empty_validation
phone_validation = non_empty_validation
# XXX urlparse allows basically anything, maybe check for existence of netloc (i.e. host) part?
url_validation = non_empty_validation & CanCallValidation(urlparse)

# Type specs are used to associate type names with validations (in the
# type_specs dictionary, below), and also to note whether to use a
# type to create suggestions (types which match any non-empty string
# make poor suggestions).  The specificity value is used to rank type
# specs: if two type specs have the same error rate for a column, the
# one with the higher specificity comes earlier in the list of
# suggestions.
class TypeSpec(object):
    def __init__(self, name, validation, specificity=50, suggest=True):
        self.name = name
        self.validation = validation
        self.specificity = specificity
        self.suggest = suggest

# Built-in type specs by column name
type_specs = {
    'percentage': TypeSpec('Percentage', percentage_validation),
    'email_address': TypeSpec('EmailAddress', email_address_validation),
    # Make plain number less specific than percentages etc
    'number': TypeSpec('Number', number_validation, specificity=30),
    'string': TypeSpec('String', string_validation, suggest=False),
    'first_name': TypeSpec('FirstName', first_name_validation, suggest=False),
    'last_name': TypeSpec('LastName', last_name_validation, suggest=False),
    'full_name': TypeSpec('FullName', full_name_validation, suggest=False),
    'middle_name': TypeSpec('MiddleName', middle_name_validation, suggest=False),
    'city': TypeSpec('City', city_validation, suggest=False),
    'business_name': TypeSpec('BusinessName', business_name_validation, suggest=False),
    'marital_status': TypeSpec('MaritalStatus', marital_status_validation),
    'ip4': TypeSpec('Ip4', ip4_validation),
    # Lat and lon have specificities mainly to make tests deterministic:
    # Giving them specificities 49 and 48 ensures they appear in that order
    # and after percentage, which has default specificity of 50.
    'latitude': TypeSpec('Latitude', latitude_validation, specificity=49),
    'longitude': TypeSpec('Longitude', longitude_validation, specificity=48),
    'domain': TypeSpec('Domain', domain_validation),
    'year_month': TypeSpec('YearMonth', year_month_validation),
    'year': TypeSpec('Year', year_validation),
    'country': TypeSpec('Country', country_validation),
    # Make these codes more specific than numbers, percentages, etc.
    'us_ein': TypeSpec('UsEin', us_ein_validation, specificity=70),
    'us_ssn': TypeSpec('UsSsn', us_ssn_validation, specificity=70),
    'us_ssn4': TypeSpec('UsSsn4', us_ssn4_validation, specificity=70),
    'sic_code': TypeSpec('SicCode', sic_code_validation, specificity=70),
    'gender': TypeSpec('Gender', gender_validation),
    # Make post code even more specific
    'post_code': TypeSpec('PostCode', post_code_validation, specificity=90),
    'state': TypeSpec('State', state_validation, specificity=90),
    'street': TypeSpec('Street', street_validation, suggest=False),
    'blob': TypeSpec('Blob', blob_validation, suggest=False),
    'phone': TypeSpec('Phone', phone_validation, suggest=False),
    'url': TypeSpec('Url', url_validation, suggest=False)
}
# Invert the builtin type specs for quick access by type name
type_specs_by_name = {
    ts.name : ts for col, ts in type_specs.items()
}
# Like type_specs, but includes all columns from all
# providers.  Computed lazily if required by validation code.
all_type_specs = None

# Type suggestions are generated for each column whose name doesn't
# match one of our predefined column names.  Each suggestion points to
# a potential type spec and has an error rate (float, percentage) that
# says how many rows of that column didn't pass that type spec's
# validation.
class TypeSuggestion(object):
    def __init__(self, type_spec, error_rate):
        self.type_spec = type_spec
        self.error_rate = error_rate
    def __repr__(self):
        return self.type_spec.name + " (hit rate: {:.1f}%)".format(100 - self.error_rate)

# A message suggestion is used to tell the user something about a
# column if we can't create or find a type suggestion.
class MessageSuggestion(object):
    def __init__(self, message):
        self.message = message
    def __repr__(self):
        return self.message

# New validation object optimized for understandability, to replace
# Validation.  Simply iterates through all columns of the input
# dataframe, and for each does some checks.  The result of the checks
# is a status object describing the column (see the classes ending in
# "Status" below).
class Validation(object):
    def __init__(self, inputs, providers, config):
        self.config = config
        self.init_type_specs()
        # Create per-column statuses for all columns of input DF
        self.statuses = []
        for col in list(inputs):
            if not col in all_type_specs:
                self.statuses.append(NotRecognizedColumnStatus(col))
            elif not is_string_dtype(inputs[col]):
                self.statuses.append(NotAStringColumnStatus(col))
            else:
                regex_validation = all_type_specs[col].validation
                validation_series = regex_validation.validate(inputs[col])
                num_ok = validation_series.sum() # counts all Trues as 1, False as 0
                num_total = len(inputs)
                if num_ok == num_total:
                    self.statuses.append(OKColumnStatus(col))
                else:
                    num_failed = num_total - num_ok
                    # ahem
                    failed_example_index = validation_series[validation_series==False].index[0]
                    failed_example = inputs[col][failed_example_index]
                    status = ValidationFailedColumnStatus(col, num_failed, num_total, failed_example)
                    self.statuses.append(status)
        # Create per-provider status
        self.provider_statuses = []
        for p in providers:
            self.provider_statuses.append(self.create_provider_status(p, inputs))

    # Build mapping of all columns supported by all providers to the
    # type spec of each column.
    def init_type_specs(self):
        global all_type_specs
        if all_type_specs == None:
            all_type_specs = dict(type_specs)
            providers = self.config.all_providers()
            for p in providers:
                version = p["version"]
                if version:
                    for input_field in version["input_fields"]:
                        name = input_field["name"]
                        type = input_field["type"]
                        # Don't overwrite existing columns
                        if not name in all_type_specs:
                            if type in type_specs_by_name:
                                all_type_specs[name] = type_specs_by_name[type]

    def create_provider_status(self, provider_name, inputs):
        return ProviderStatus(provider_name, inputs, self.config)

    def all_valid(self):
        for status in self.statuses:
            if not isinstance(status, OKColumnStatus):
                return False
        for provider_status in self.provider_statuses:
            if not provider_status.valid():
                return False
        return True

    def _repr_html_(self):
        doc, tag, text, line = Doc().ttl()
        # Render per-column statuses
        if (len(self.statuses) > 0):
            with tag("table"):
                with tag("tr"):
                    with tag("th"):
                        text("Column")
                    with tag("th"):
                        text("Status")
                    with tag("th"):
                        text("Description")
                for status in self.statuses:
                    status.render(doc, tag, text, line)
        # Render provider statuses
        if (len(self.provider_statuses) > 0):
            line("h3", "Providers")
            with tag("table"):
                with tag("tr"):
                    with tag("th"):
                        text("Provider")
                    with tag("th", style="text-align: left"):
                        text("Status")
                for provider_status in self.provider_statuses:
                    provider_status.render(doc, tag, text, line)
        return doc.getvalue()

# Abstract superclass of per-column statuses.
class ColumnStatus(object):
    pass

# If a column is not even a string, we tell the user they must convert
# it to a string.
class NotAStringColumnStatus(ColumnStatus):
    def __init__(self, col):
        self.col = col
    def render(self, doc, tag, text, line):
        with tag("tr"):
            with tag("th"):
                text(self.col)
            with tag("td", style="background-color: lightpink"):
                with tag("nobr"):
                    text("Not a String Column")
            with tag("td", style="text-align: left"):
                text("You must convert this column to string type.")

# If we don't understand the column name, we point the user to the
# online documentation page with the list of all supported column
# names.
class NotRecognizedColumnStatus(ColumnStatus):
    def __init__(self, col):
        self.col = col
    def render(self, doc, tag, text, line):
        with tag("tr"):
            with tag("th"):
                text(self.col)
            with tag("td", style="background-color: lightpink"):
                with tag("nobr"):
                    text("Unrecognized Column Name")
            with tag("td", style="text-align: left"):
                text("This column name is not supported. ")
                with tag("a", href="https://demyst.com/docs/demyst-live/types/", target="_blank"):
                    text("Click here for a list of all supported column names.")

# If one or more column values didn't pass the regex-based validation,
# we give the the percentage of failed values.  We also point them to
# the online documentation section for that column.
class ValidationFailedColumnStatus(ColumnStatus):
    def __init__(self, col, num_failed, num_total, failed_example):
        self.col = col
        self.num_failed = num_failed
        self.num_total = num_total
        self.failed_example = failed_example
    def render(self, doc, tag, text, line):
        if self.num_failed == self.num_total:
            with tag("tr"):
                with tag("th"):
                    if self.col in type_specs:
                        with tag("a", href="https://demyst.com/docs/demyst-live/types/#" + self.col, target="_blank"):
                            text(self.col)
                    else:
                        text(self.col)
                with tag("td", style="background-color: lightpink"):
                    with tag("nobr"):
                        text("All Invalid")
                with tag("td", style="text-align: left"):
                    text("None of the " + str(self.num_total) +
                         " column value(s) passed validation. ")
                    text("One example of an invalid value is '" + str(self.failed_example) + "'. ")
                    with tag("a", href="https://demyst.com/docs/demyst-live/types/#" + self.col, target="_blank"):
                        text("Click here for documentation for this column.")
        else:
            with tag("tr"):
                with tag("th"):
                    if self.col in type_specs:
                        with tag("a", href="https://demyst.com/docs/demyst-live/types/#" + self.col, target="_blank"):
                            text(self.col)
                    else:
                        text(self.col)
                with tag("td", style="background-color: peachpuff"):
                    with tag("nobr"):
                        text("Some Invalid")
                with tag("td", style="text-align: left"):
                    percent_failed = "{:.1f}%".format(100 * float(self.num_failed) / float(self.num_total))
                    text(percent_failed + " of the values of this column failed validation. ")
                    text("One example of an invalid value is '" + str(self.failed_example) + "'. ")
                    with tag("a", href="https://demyst.com/docs/demyst-live/types/#" + self.col, target="_blank"):
                        text("Click here for documentation for this column.")


# If the column was recognized, and all values passed the validation,
# we congratulate the user.
class OKColumnStatus(ColumnStatus):
    def __init__(self, col):
        self.col = col
    def render(self, doc, tag, text, line):
        with tag("tr"):
            with tag("th"):
                if self.col in type_specs:
                    with tag("a", href="https://demyst.com/docs/demyst-live/types/#" + self.col, target="_blank"):
                        text(self.col)
                else:
                    text(self.col)
            with tag("td", style="background-color: lightgreen"):
                with tag("nobr"):
                    text("All Valid")
            with tag("td", style="text-align: left"):
                text("All values in this column are good to go.")

class ProviderStatus(object):
    def __init__(self, provider_name, inputs, config):
        self.config = config;
        self.provider_name = provider_name
        self.provider = config.lookup_provider(provider_name)
        self.inputs = inputs

    def render(self, doc, tag, text, line):
        if self.provider:
            with tag("tr"):
                with tag("th", style="vertical-align: top"):
                    text(self.provider_name)
                with tag("td", style="vertical-align: top; text-align: left"):
                    self.render_provider_inputs(self.provider, self.inputs, doc, tag, text, line)
        else:
            with tag("tr"):
                with tag("th"):
                    text(self.provider_name)
                with tag("td", style="background-color: lightpink"):
                    text("Unrecognized provider name.")

    def valid(self):
        cols = list(self.inputs)
        if type(self.provider["version"]) is dict:
            version = self.provider["version"]
            for data in version["schema"]:
                for variant in data["input"]["required"]:
                    for input in variant:
                        name = input["name"]
                        if not (name in cols):
                            return False
        return True

    def render_provider_inputs(self, provider, inputs, doc, tag, text, line):
        cols = list(inputs)
        if type(provider["version"]) is dict:
            version = provider["version"]
            for data in version["schema"]:
                for variant in data["input"]["required"]:
                    with tag("table", style="display: inline-block; margin-right: 1em"):
                        for input in variant:
                            with tag("tr"):
                                name = input["name"]
                                if name in cols:
                                    style = "background-color: lightgreen; text-align: left"
                                else:
                                    style = "background-color: #ddd; text-align: left"
                                with tag("td", style=style):
                                    with tag("a", href="https://demyst.com/docs/demyst-live/types/#" + name, target="_blank"):
                                        text(name)

class Analytics(object):

    def __init__(self, inputs=None, config_file=None, region=None, env=None, key=None, username=None, password=None, jwt=None):
        if inputs is None:
            inputs = {}
        self.__config = load_config(config_file=config_file, region=region, env=env, key=key, username=username, password=password, jwt=jwt)
        self.__key = self.__config.get("API_KEY")
        self.__prefix = True
        self.__inputs = inputs
        self.__sample_mode = False # Anchovy does not support sample mode

        # This is only used for validate and batch, so force sample_mode
        self.__connectors = Connectors(config=self.__config,
                                     inputs=self.__inputs,
                                     sample_mode=True)

        self.__print_startup_trial_message()

    def __get(self, provider_name, query, default=None, inputs=None):
        return self.__connectors.get(provider_name, query, default,
                                   inputs=inputs,
                                   shape="table", prefix=self.__prefix)

    def __field_names_from_stats():
        categorical_stats["full_field_name"] = categorical_stats["product"].map(str) + "." + categorical_stats["flattened_name"]
        flattened_field_names = list(set(categorical_stats["full_field_name"].values))
        flattened_field_names

    def input_file(self, table_name, row_limit=None, filters=None):
        return track_function(lambda: self.__do_input_file(table_name, row_limit, filters),
                              self.__config, "API : Python : Rosefish Export")

    def __do_input_file(self, table_name, row_limit=None, filters=None):
        params = { "table_name": table_name }
        if(row_limit):
            params["row_limit"] = row_limit
        if(filters):
            params["filters"] = filters
        resp = self.__config.auth_post(self.__config.get("MANTA_URL") + "export_hosted_input", json=params).json()
        link = resp["presigned_s3_get_url"]
        input_file_df = pd.read_csv(link)
        numerified_columns = ["post_code", "business_post_code", "naics_code"]
        for col in numerified_columns:
            if(col in input_file_df.columns):
                input_file_df[col] = input_file_df[col].astype(str)
        return(input_file_df)

    def input_files(self, headers=None):
        return track_function(lambda: self.__do_input_files(headers),
                              self.__config, "API : Python : Rosefish Product List")

    def __do_input_files(self, headers):
        table_providers = self.__config.auth_get(self.__config.get("MANTA_URL") + "list_hosted_inputs").json()
        if(headers):
            filtered_providers = []
            for provider in table_providers:
                output_fields = provider["output_fields"]
                output_field_names = list(map(lambda output_field: output_field["name"], output_fields))
                if all(elem in output_field_names for elem in headers):
                    filtered_providers.append(provider)
        else:
            filtered_providers = table_providers
        return list(map(lambda provider: provider['name'], filtered_providers))

    def input_file_headers(self, table_name):
        return track_function(lambda: self.__do_input_file_headers(table_name),
                              self.__config, "API : Python : Rosefish Product Headers")

    def __do_input_file_headers(self, table_name):
        table_providers = self.__config.auth_get(self.__config.get("MANTA_URL") + "list_hosted_inputs").json()
        provider_names = list(map(lambda provider: provider['name'], table_providers))
        if table_name in provider_names:
            headers = [provider["output_fields"] for provider in table_providers if provider['name'] == table_name][0]
            header_df = pd.DataFrame(headers)
            return(header_df.filter(items=['name', 'description', 'json_type_name']))
        else:
            print("Warning: could not find input file: {}".format(table_name), file=sys.stderr)

    def list_stats_products(self):
         return track_function(lambda: self.__do_list_stats_products(),
                              self.__config, "API : Python : Hogfish Product List")

    def __do_list_stats_products(self):
        return self.__config.auth_get(self.__config.get("MANTA_URL") + "hogfish_providers").json()


    def product_stats(self, provider_names=[], all_products=False):
        return track_function(lambda: self.__do_product_stats(provider_names, all_products),
                              self.__config, "API : Python : Hogfish Stats",
                              { "provider_names": provider_names,
                                "all_products": all_products })

    
    def __do_product_stats(self, provider_names, all_products):
        res = []
        if all_products:
            provider_names = self.list_stats_products()
        for provider_name in provider_names:
            print("Getting stats for " + provider_name)
            res = res + self.__call_manta_hogfish(provider_name)
        df_res = pd.DataFrame(res)
        self.__fixup_hogfish_df(df_res)
        if "id" in df_res:
            df_res.drop(columns=['id'], inplace=True)
        if "provider_id" in df_res:
            df_res.rename(columns = {'provider_id':'product'}, inplace = True)
        if (("flattened_name" in df_res) and ("product" in df_res)):
            df_res["full_field_name"] = df_res["product"].map(str) + "." + df_res["flattened_name"]
        df_res.rename(columns={'consistency_rate':'attribute_consistency_rate','entity_name':'input_entity','error_rate':'product_error_rate','field_is_populated_rate':'attribute_fill_rate','flattened_name':'attribute_flattened_name','generic_flattened_name':'attribute_generic_name','hit_rate':'product_match_rate','num_distinct_values':'attribute_unique_values','full_field_name':'attribute_full_name', 'last_updated_at': 'stats_updated_on', 'max_val': 'max_value', 'min_val': 'min_value', 'standard_deviation': 'std'}, inplace = True)
        self.__add_extra_stats_columns(df_res)
        # Reorder columns
        return(df_res[[
                    'input_entity',
                    'stats_updated_on',
                    'product',
                    'product_error_rate',
                    'product_match_rate',
                    'attribute_flattened_name',
                    'attribute_fill_rate',
                    'attribute_consistency_rate',
                    'attribute_unique_values',
                    'most_common_values',
                    'std',
                    'median',
                    'mean',
                    'max_value',
                    'variance',
                    'min_value',
                    'attribute_onboarded_date',
                    'attribute_audited_date',
                    'attribute_pii',
                    'attribute_use_case'
                    ]])
    
    def __add_extra_stats_columns(self, df):
        public_providers_list = self.__config.auth_get(self.__config.get("MANTA_URL") + "public/providers").json()
        public_providers = {}
        for pp in public_providers_list:
            public_providers[pp["name"]] = pp
        def extract_attribute_onboarded_date(row):
            return public_providers[row.at["product"]]["created_at"]
        def extract_attribute_audited_date(row):
            return row.at["stats_updated_on"]
        pii_regex = re.compile(r'(?i)(city|state|address|zip|post_code|postcode|location|locality|list_date|latitude|longitude|delivery_point|carrier_route|name|first_name|full_name|last_name|middle_name|suffix|phone|email|ssn|price|date_of_birth|date_of_death|contact|sms|court_case|sex_offender|deceased|age|owner|relation|gender|infoprivacy|tax|legal|market_value|assessed_value|business_name|businessname|companyname)')
        def extract_attribute_pii(row):
            if pii_regex.search(row.at["attribute_flattened_name"]):
                return 1
            else:
                return 0
        def extract_attribute_use_case(row):
            return ", ".join(map(lambda tag: tag["name"], self.__config.lookup_provider(row.at["product"])["tags"]))
        df["attribute_onboarded_date"] = df.apply(extract_attribute_onboarded_date, axis=1)
        df["attribute_audited_date"] = df.apply(extract_attribute_audited_date, axis=1)
        df["attribute_pii"] = df.apply(extract_attribute_pii, axis=1)
        df["attribute_use_case"] = df.apply(extract_attribute_use_case, axis=1)

    # In stg, we're missing Hogfish results.  Default columns.
    def __fixup_hogfish_df(self, df):
        cols = list(df)
        def ensure_col(name, value):
            if not name in cols:
                print("Warning: adding column: " + name, file=sys.stderr)
                df[name] = value
        def ensure_nan_col(name):
            ensure_col(name, np.nan) 
        ensure_nan_col("standard_deviation")
        ensure_nan_col("min_val")
        ensure_nan_col("max_val")
        ensure_nan_col("variance")
        ensure_nan_col("mean")
        ensure_nan_col("median")
        ensure_col("most_common_values", "{}")

    def __call_manta_hogfish(self, provider_name):
        input = {
            "table_provider": provider_name,
        }
        try:
            res = self.__config.auth_post(self.__config.get("MANTA_URL") + "hogfish_stats", json=input)
        except RuntimeError as e:
            error_response = e.args[0]
            if error_response == 'Error while making HTTP request: 400 {"error":"Stats not found"}':
                print("Warning: stats not found for data provider: {}".format(provider_name), file=sys.stderr)
            elif error_response == 'Error while making HTTP request: 400 {"error":"Table provider not found"}':
                print("Warning: Data Provider {} not found".format(provider_name), file=sys.stderr)
            return([])
        return(res.json())

    def data_function_append(self, name, inputs_dframe):
        return track_function(lambda: self.__do_data_function_append(name, inputs_dframe),
                              self.__config, "API : Python : Data Function Append",
                              { "name": name })

    def __do_data_function_append(self, name, inputs_dframe):
        # TODO: call async
        non_nan_dframe = inputs_dframe.replace(np.nan, '', regex=True)
        output = [None] * len(non_nan_dframe)
        for idx, row in progressbar(non_nan_dframe.iterrows()):
            inputs = dict([(key, row[key]) for key in row.keys()])
            output[idx] = inputs
            post = {
                "inputs": inputs,
                "providers": [],
                "data_function_id": name
            }
            channel_url = self.__config.get("BLACKFIN_URL") + "v2/execute"
            resp = self.__config.auth_post(channel_url,
                                    json=post,
                                    headers={'Content-Type':'application/json'},
                                    flags={"for_blackfin":True})
            body = resp.json()
            result = body['pipes']['data_function']['result']
            output[idx] = {**output[idx], **result}

        appended_dframe = pd.DataFrame.from_dict(output)
        sorted_columns = list(inputs_dframe.columns) + [x for x in appended_dframe.columns if x not in list(inputs_dframe.columns)]
        return appended_dframe[sorted_columns]

    # Use this to fetch sample data for a list of providers.  The
    # input dataframe is validated but ignored, it should have (at
    # least) one row.
    def fetch_sample_data(self, providers, inputs_dframe):
        row = inputs_dframe.iloc[0,:] # Only need one row
        inputs = dict([(key, row[key]) for key in row.keys()])
        no_failures = self.__connectors.fetch(providers, inputs=inputs, sample_mode=True)
        if not no_failures:
            for provider_name in providers:
                provider_error = self.__connectors.cache_get_error(provider_name, inputs)
                if provider_error:
                    print("Transaction with %s failed because of %s: %s. "%(provider_name, provider_error['type'], provider_error['message']), file=sys.stderr)
        # Concat results
        df = inputs_dframe.head(1)
        for provider_name in providers:
            provider_data = self.__connectors.get(provider_name, '', inputs=inputs, shape="table", prefix=True)
            if provider_data:
                provider_df = pd.DataFrame.from_dict([provider_data])
                df = pd.concat([df, provider_df], axis="columns")
        return df

    # Easy-to-use frontend to enrich, enrich_wait, and enrich_download
    def enrich_and_download(self, providers, inputs=None, hosted_input=None, validate=True, all_updates=False, fixed_list_size=None):
        id = self.enrich(providers,
                         inputs=inputs,
                         hosted_input=hosted_input,
                         validate=validate,
                         all_updates=all_updates,
                         fixed_list_size=fixed_list_size)
        return self.enrich_download(id)

    def enrich_with_hosted_inputs(self, providers, hosted_input, row_limit=None, filters=None):
        inputs = self.input_file(hosted_input, row_limit=row_limit, filters=filters)
        return self.enrich_and_download(providers=providers, inputs=inputs, validate=False)

    def enrich(self, providers, inputs=None, hosted_input=None, validate=True, all_updates=False, fixed_list_size=None):
        if hosted_input:
            inputs = self.input_file(hosted_input)
        self.__check_provider_names(providers)
        return track_function(lambda: self.__do_enrich(providers,
                                                     inputs,
                                                     validate=validate,
                                                     all_updates=all_updates,
                                                     fixed_list_size=fixed_list_size),
                              self.__config, "API : Python : Enrich",
                              { "provider_names": providers,
                                "num_rows": len(inputs) })

    def enrich_credits(self, providers, inputs, validate=True):
        self.__check_provider_names(providers)
        inputs = self.__stringify_dframe(inputs)
        if (validate):
            if (not self.__validate_providers(providers, inputs)):
                return None
        provider_ids = [self.__config.provider_name_to_id(name) for name in providers]
        num_rows = len(inputs)
        url_params = { "rows": num_rows, "providers[]": provider_ids }
        path = "table_providers/calculate_credit_cost?" + urlencode(url_params, doseq=True)
        return self.__config.auth_get(self.__config.get("MANTA_URL") + path).json()["total_cost"]

    def __do_enrich(self, providers, inputs, validate=True, all_updates=False, fixed_list_size=None):
        print("Starting enrichment...")
        inputs = self.__stringify_dframe(inputs)
        if (validate):
            if (not self.__validate_providers(providers, inputs)):
                raise RuntimeError("Validation failed")
        fd, temp_path = tempfile.mkstemp()
        try:
            inputs.to_csv(temp_path, index=False, header=False, quoting=csv.QUOTE_ALL)
            return self.__enrich_csv(providers, temp_path, list(inputs), all_updates, fixed_list_size)
        finally:
            os.close(fd)
            try:
                os.remove(temp_path)
            except Exception as e:
                #print("Warning: couldn't delete temporary file: " + temp_path, file=sys.stderr)
                pass

    def __enrich_csv(self, providers, csv_file, columns, all_updates, fixed_list_size):
        num_rows = self.__count_lines_in_file(csv_file)
        if not self.__has_enough_caps(providers, num_rows):
            return
        region_id = self.__find_region_id(self.__config.get("REGION"))
        dict = self.__get_presigned_url_and_s3_object_key(region_id)
        url = dict["presigned_url"]
        s3_key = dict["s3_object_key"]
        self.__upload_file_to_presigned_url(csv_file, url)
        input_id = self.__create_batch(csv_file, s3_key, columns, region_id, num_rows)
        run_batch_id = self.__run_batch(providers, input_id, region_id, all_updates, fixed_list_size)
        print("Enrich Job ID: " + str(run_batch_id))
        return run_batch_id

    def __upload_file_to_presigned_url(self, csv_file, url):
        #print("Uploading data...")
        with open(csv_file, "rb") as f:
            res = requests.put(url, data=f)
            if (res.status_code != 200):
                raise RuntimeError("Error while trying to upload file: " + res.text)

    def __get_presigned_url_and_s3_object_key(self, region_id):
        params = { "region_id": region_id }
        res = self.__config.auth_get(self.__config.get("MANTA_URL") + "presigned_batch_upload_url",
                              params=params)
        return res.json()

    def __create_batch(self, csv_file, s3_key, columns, region_id, num_rows):
        input = {
            "aegean_batch_input": {
                "name": csv_file,
                "num_rows": num_rows,
                "region_id": region_id,
                "s3_object_key": s3_key,
                "headers": columns
            }
        }
        res = self.__config.auth_post(self.__config.get("MANTA_URL") + "aegean_batch_inputs", json=input)
        return res.json()["id"]

    def __find_region_id(self, region_code):
        region_json = self.__config.auth_get(self.__config.get("MANTA_URL") + "list_regions").json()
        for region in region_json:
            if region["code"] == region_code:
                return region["id"]
        raise RuntimeError("Region not found: " + region_code)

    def __run_batch(self, providers, input_id, region_id, all_updates, fixed_list_size):
        provider_ids = [self.__config.provider_name_to_version_id(name) for name in providers]
        if self.__config.has("API_KEY"):
            username = self.__config.get("API_KEY")[:8]
        else:
            username = self.__config.get_username()
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        name = "{}--{}--{}".format(username, "--".join(providers), timestamp)
        # Send draft request to get org credits info
        input = {
            "aegean_batch_run": {
                "aegean_batch_input_id": input_id,
                "provider_version_ids": provider_ids,
                "region_id": region_id,
                "name": name,
                "draft": True,
            }
        }
        if all_updates is True or all_updates is False:
            input["aegean_batch_run"]["all_updates"] = all_updates
        if fixed_list_size:
            input["aegean_batch_run"]["fixed_list_size"] = fixed_list_size
        draft_res = self.__config.auth_post(self.__config.get("MANTA_URL") + "aegean_batch_runs",
                                     json=input).json()
        org_credits = draft_res["organization"]["credit_balance"]
        run_credits = draft_res["estimated_credit_cost"]
        #self.__print_credits(draft_res)
        if (self.__config.get_credits_or_caps() == "credits") and (org_credits < run_credits):
            raise RuntimeError("Aborting due to insufficient credits.")
        else:
            # Update to non-draft status
            input["aegean_batch_run"]["draft"] = False
            res = self.__config.auth_put(self.__config.get("MANTA_URL") + "aegean_batch_runs/" + str(draft_res["id"]),
                                  json=input).json()
            return res["id"]

    def __print_credits(self, batch_run_resp):
        if self.__sample_mode:
            print("This enrichment will cost 0 credits because you are using sample data.",
                  file=sys.stderr)
            print("To switch to live mode, please set sample_mode=False in the Analytics class.",
                  file=sys.stderr)
        else:
            org_credits = "{:n}".format(batch_run_resp["organization"]["credit_balance"])
            run_credits = "{:n}".format(batch_run_resp["estimated_credit_cost"])
            #print("This enrichment will use " + run_credits + " credits of the " + org_credits + " credits your organization currently has.", file=sys.stderr)

    def __has_enough_caps(self, provider_names, num_rows):
        if self.__config.get_credits_or_caps() == "caps":
            cap_items = self.__get_cap_items(provider_names)
            return self.__check_cap_items(cap_items, num_rows)
        else:
            return True

    def __get_cap_items(self, provider_names):
        items = []
        page = 1
        while True:
            params = { "page": page, "table_provider_names[]": provider_names }
            resp = self.__config.auth_get(self.__config.get("MANTA_URL") + "table_providers/cap_status", params=params).json()
            if resp == []:
                return items
            else:
                items.extend(resp)
                page = page + 1

    def __check_cap_items(self, items, num_rows):
        providers_with_too_few_caps = []
        for item in items:
            cap = item["monthly_cap"]
            current = item["current_transaction_count"]
            if cap != None:
                if (current + num_rows) > cap:
                    providers_with_too_few_caps.append(item)
        if len(providers_with_too_few_caps) > 0:
            message = "Aborting due to insufficient provider caps: " + str(num_rows) + " needed. "
            for p in providers_with_too_few_caps:
                left = p["monthly_cap"] - p["current_transaction_count"]
                if left < 0:
                    left = 0
                message += (p["table_provider_name"] + " has " + str(left) + " left. ")
            print(message, file=sys.stderr)
            return False
        else:
            return True

    def __count_lines_in_file(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    # Return true if all providers are done, false otherwise.
    def enrich_status(self, id, notebook=True):
        resp_json = self.__fetch_enrich_status(id)
        if notebook:
            print(self.__enrich_status_message(resp_json))
        return self.__enrich_status_finished(resp_json)

    def enrich_wait(self, id):
        # This progress bar is fake, but still an effective UI
        # element.  It starts at 50% and stays there until finished,
        # then we set it to 100%.
        bar = widgets.IntProgress(value=1,min=0,max=2)
        label = widgets.HTML("Checking status...")
        display(bar)
        display(label)
        while True:
            resp_json = self.__fetch_enrich_status(id)
            if self.__enrich_status_finished(resp_json):
                label.value = "Done."
                bar.value = 2
                return
            else:
                label.value = self.__enrich_status_message(resp_json)
                sleep(5)

    def __fetch_enrich_status(self, id):
        return self.__config.auth_get(self.__config.get("MANTA_URL") + "aegean_batch_runs/" + str(id)).json()

    # Check that all export links are available
    def __enrich_status_finished(self, resp_json):
        if resp_json["state"] == "pending_approval":
            raise RuntimeError("It looks like you do not have permissions to run live enrichments. Please contact support@demystdata.com for help.")
        for provider in resp_json["batch_run_provider_versions"]:
            if not provider["most_recent_export_link"]:
                return False
        return True

    # For each provider X, create a message like "X (55%)" or "X
    # (exporting)" or "X (done)".
    def __enrich_status_message(self, resp_json):
        num_rows = resp_json["num_rows"]
        messages = []
        for provider in resp_json["batch_run_provider_versions"]:
            name = provider["table_provider"]["name"]
            rows_completed = provider["rows_completed"] or 0
            status = "done"
            if rows_completed < num_rows:
                status = "{:.1f}%".format(100 * float(rows_completed) / float(num_rows))
            elif not provider["most_recent_export_link"]:
                status = "exporting"
            messages.append(name + " (" + status + ")")
        return "<br>".join(messages)

    def enrich_download(self, id, block_until_complete=True):
        return track_function(lambda: self.__do_enrich_download(id, block_until_complete=block_until_complete),
                              self.__config, "API : Python : Download",
                              { "job_id": id })

    def __do_enrich_download(self, id, block_until_complete=True):
        fd, temp_path = tempfile.mkstemp()
        try:
            # Overwrite=True is needed because temp file gets created above
            self.enrich_download_to_disk(id,
                                         temp_path,
                                         overwrite=True,
                                         block_until_complete=block_until_complete)
            return pd.read_csv(temp_path, na_filter=False)
        finally:
            os.close(fd)
            try:
                os.remove(temp_path)
            except Exception as e:
                #print("Warning: couldn't delete temporary file: " + temp_path, file=sys.stderr)
                pass

    def enrich_download_to_disk(self, id, file_path, overwrite=False, block_until_complete=True):
        if not overwrite:
            if os.path.isfile(file_path):
                raise RuntimeError("File exists: " + file_path)
        if block_until_complete:
            self.enrich_wait(id)
        resp_json = self.__config.auth_get(self.__config.get("MANTA_URL") + "aegean_batch_runs/" + str(id)).json()
        provider_results = resp_json["batch_run_provider_versions"]
        # Gather all exports
        exports = [] # list of { provider_name, export_link, temp_fd, temp_path }
        for r in provider_results:
            export_link = r["most_recent_export_link"]
            if export_link:
                provider_name = r["table_provider"]["name"]
                temp_fd, temp_path = tempfile.mkstemp(prefix=provider_name, suffix=".csv")
                exports.append({ "provider_name": provider_name,
                                 "export_link": export_link,
                                 "temp_fd": temp_fd,
                                 "temp_path": temp_path })
            else:
                print("Provider " +provider_name+ " has not finished enrichment and will not be included." , file=sys.stderr)
        # Download all export links to temp files in parallel
        def fetch_export(export):
            r = requests.get(export["export_link"], stream=True)
            if r.status_code == 200:
                with open(export["temp_path"], "wb") as f:
                    for chunk in r:
                        f.write(chunk)
            else:
                raise RuntimeError("Download of file " + export["export_link"] + " failed: " + str(r.status_code))
        try:
            # Download
            pool = ThreadPool(16)
            pool.imap_unordered(fetch_export, exports)
            pool.close()
            pool.join()
            # Merge files
            self.__merge_csv_files(exports, file_path)
        finally:
            for export in exports:
                os.close(export["temp_fd"])
                try:
                    os.remove(export["temp_path"])
                except Exception as e:
                    #print("Warning: couldn't delete temporary file: " + export["temp_path"], file=sys.stderr)
                    pass

    # Reads the temp CSV files and writes them to an output file in chunks
    def __merge_csv_files(self, exports, out_file):
        for export in exports:
            export["iterator"] = pd.read_csv(export["temp_path"], chunksize=100, na_filter=False)
        try:
            # Disable universal newlines to prevent empty lines on Windows
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                header = True # Only print header for first chunk
                while True:
                    df = pd.DataFrame({})
                    returned_inputs = None
                    # Mung the data
                    for export in exports:
                        provider_df = export["iterator"].get_chunk()
                        input_cols = [c for c in provider_df.columns if c.startswith("inputs.")]
                        # Extract inputs passed through by provider
                        if returned_inputs is None:
                            returned_inputs = provider_df[input_cols]
                        # Drop the inputs from the dataframe
                        provider_df = provider_df.drop(input_cols, axis="columns")
                        # Prefix all remaining columns with provider name
                        provider_df = provider_df.rename(lambda col: export["provider_name"] + "." + col,
                                                         axis="columns")
                        df = pd.concat([df, provider_df], axis="columns")
                    if df.empty:
                        print("No results were returned from this enrichment", file=sys.stderr)
                    # Add inputs to final dataframe
                    df = pd.concat([returned_inputs, df], axis="columns")
                    # Write chunk (without index column)
                    df.to_csv(f, index=False, header=header, quoting=csv.QUOTE_ALL)
                    if header:
                        header = False
        except StopIteration as stop:
            return

    def search(self, inputs=None, hosted_input=None, tags=None, view="html", strict=False):
        if hosted_input:
            inputs = self.input_file(hosted_input)
        if isinstance(inputs, pd.DataFrame):
            inputs = list(inputs)
        return track_function(lambda: self.__do_search(inputs=inputs, tags=tags, view=view, strict=strict),
                              self.__config, "API : Python : Search",
                              { "tags": tags, "view": view, "inputs": inputs })

    def __do_search(self, inputs=None, tags=None, view="html", strict=False):
        if isinstance(inputs, list) or isinstance(tags, list):
            params = {
                'inputs[]': inputs,
                'tags[]': tags
                }
            murl = "%stable_providers/match_given_input.json" % self.__config.get("MANTA_URL")
            response = self.__config.auth_get(murl, params=params)
            connectors = response.json()
        elif isinstance(inputs, str):
            providers = self.__search_unguided(inputs)
            connectors = [self.__transform_provider_to_connector(p) for p in providers]
        else:
            providers = self.__config.all_providers()
            connectors = [self.__transform_provider_to_connector(p) for p in providers]
        if strict:
            connectors = self.__filter_connectors_strictly(connectors, inputs)
        if (view == "html"):
            return self.__render_connectors(connectors, inputs)
        elif (view == "json"):
            return connectors
        elif (view == "dataframe"):
            return self.product_inputs([c["name"] for c in connectors], view="dataframe")
        else:
            raise RuntimeError("View must be html, json, or dataframe.")

    # Search product name, category, and tags of all providers for query string
    def __search_unguided(self, query):
        query = query.lower()
        providers = self.__config.all_providers()
        results = []
        for p in providers:
            sources = []
            sources.append(p["name"].lower())
            sources.append(p["category"].lower())
            for tag in p["tags"]:
                sources.append(tag["name"].lower())
            for s in sources:
                if query in s:
                    results.append(p)
                    break
        return results

    def __render_connectors(self, connectors, inputs):
        doc, tag, text, line = Doc().ttl()
        table = {}
        if connectors == []:
            line('p', "Sorry, we couldn't find any Data Products that matched this input.", style='font-style: italic;')
        else:
            for connector in connectors:
                connector_inputs = list(set(list(itertools.chain(*connector['required_input_name_sets']))))
                with tag('div', style=''):
                    with tag('div', style="pading:10px;"):
                        with tag('div',style='padding:5px'):
                            with tag('h1'):
                                doc.stag('img', height=30, width=30, src=connector['data_source_logo_url'], style="display:inline-block")
                                text(" " + connector['data_source_name'])
                            line('pre', connector['name'], style='')
                            with tag('p'):
                                if connector['description']:
                                    line('em', connector['description'])
                        with tag('div', style='padding: 5px;'):
                            with tag('table'):
                                with tag('tr'):
                                    with tag('th'):
                                        text(" ")
                                    for i in range(len(connector_inputs)):
                                        with tag('th'):
                                            text(connector_inputs[i])
                                for ri_idx, required_inputs in enumerate(connector['required_input_name_sets']):
                                     with tag('tr'):
                                        with tag('td'):
                                            text("Option " + str(ri_idx + 1))
                                        for i in range(len(connector_inputs)):
                                            with tag('td'):
                                                with tag('span', style="font-size: 20px;"):
                                                    if connector_inputs[i] in required_inputs:
                                                        if inputs and (connector_inputs[i] in inputs):
                                                            text("☒")
                                                        else:
                                                            text("☐")
                                                    else:
                                                        text(" ")
        return HTML(doc.getvalue())

    def __filter_connectors_strictly(self, connectors, inputs):
        input_set = set(inputs)
        def any_required_input_matches(connector):
            return len([r for r in connector["required_input"] if set(r).issubset(input_set)]) > 0
        return [c for c in connectors if any_required_input_matches(c)]

    def __load_demo_csv(self):
        return pd.read_csv(os.path.join(os.path.dirname(__file__), "sample/website.csv"))

    def __validate_providers(self, providers, inputs, return_errors=False):
        inputs_one_dframe = inputs[:1]
        inputs = inputs_one_dframe.to_dict('records')[0]

        try:
            success = self.__connectors.fetch(providers, inputs, sample_mode=True)
        except DemystConnectorError as e:
            d = e.args[0]
            print("Failed to run %s because of %s. Contact support@demystdata.com for help."%(d['transaction_id'], d['message']), file=sys.stderr)
            return False

        errors=[]
        if (not success):
            for provider_name in providers:
                if self.__connectors.cache_get_error(provider_name, inputs):
                    error = self.__connectors.cache_get_error(provider_name, inputs)
                    error['provider_name'] = provider_name
                    if (return_errors):
                        errors.append(error)
                    else:
                        print('%s: %s'% (provider_name, error['message']), file=sys.stderr)

        if (return_errors):
            return errors
        else:
            return success

    # Check that all providers from a list of provider names exist/are supported,
    # raise an exception if not.
    def __check_provider_names(self, providers):
        print("Verifying providers...")
        for p in providers:
            if not self.__config.lookup_provider(p):
                raise RuntimeError("Sorry, either you mistyped the product name " + p + " or your organization doesn't have access to that product.")

    def validate(self, inputs=None, providers=None, notebook=True):
        if inputs is None:
            inputs = pd.DataFrame({})
        if providers is None:
            providers = []
        validation = Validation(inputs, providers, self.__config)
        if notebook:
            return validation
        else:
            return validation.all_valid()

    def credits(self):
        headers = { "Accept": "application/json" }
        resp_json = self.__config.auth_get(self.__config.get("MANTA_URL") + "organization", headers=headers).json()
        balance = resp_json["credit_balance"]
        self.__print_credits_trial_message(balance)
        return balance

    # Print configuration settings
    def show_settings(self):
        for (key, val) in self.__config.settings.items():
            print(key + ": " + val)

    # Product catalog: simple JSON info about available providers
    def products(self, params=None, full=False, dataframe=True):
        if params is None:
            params = {}
        connectors = self.__connectors.products(full=full)
        if("stats_available" in params):
            stats_products = self.list_stats_products()
            stats_connectors = [connector for connector in connectors if connector['name'] in stats_products]
            return(stats_connectors)
        elif(dataframe):
            main_components = list(map(lambda product:
                        {'Product Name': product['name'], 'Category' : product['category'],
                         'Tags' : ", ".join(list(map(lambda tag: tag["name"], product['tags']))),
                         'Website' : product['website'], 'Description' : product['description'],
                         'Data Source' : product['data_source'], 'Regions' : ', '.join(product['regions']),
                         'FCRA' : product['fcra'], 'TLS' : product['tls'],
                         'Post Request' : product['post'],
                         'Credit Cost' : product['credit_cost'],
                         'Cost' : product['cost'], 'Recently Added' : product['recently_added'],
                         'Processing Time' : product['processing_time'],
                         'Online' :product['online'] }, connectors))
            products = pd.DataFrame(main_components, columns=main_components[0].keys())
            return(products)
        else:
            return(connectors)

    def product_catalog(self, provider_names=[], all_products=False, view="dataframe"):
        if ((provider_names == []) and not all_products):
            print("Try product_catalog(all_products=True) to see all of the available products in Demyst. Given the large list of products, we recommend installing our Analytics package in your Python environment.",
                  file=sys.stderr)
        if view == "json":
            if all_products:
                provider_names = self.__config.all_provider_names()
            results = {}
            for provider_name in provider_names:
                catalog = self.__connectors.product_catalog(provider_name)
                if catalog:
                    results[provider_name] = catalog
            return results
        elif view == "dataframe":
            inputs = self.product_inputs(provider_names, all_products=all_products)
            outputs = self.product_outputs(provider_names, all_products=all_products)
            return pd.concat([inputs, outputs], ignore_index=True)
        else:
            raise RuntimeError("View must be dataframe or json.")

    def product_inputs(self, provider_names=[], all_products=False, view="dataframe"):
        if all_products:
            provider_names = self.__config.all_provider_names()
        if view == "dataframe":
            result = []
            for provider_name in provider_names:
                catalog = self.__connectors.product_catalog(provider_name)
                if catalog:
                    counter = 1
                    for c in catalog:
                        for req_inputs in c["input"]["required"]:
                            option = "option" + str(counter)
                            self.__collect_inputs(provider_name, req_inputs, option, result, "")
                            counter += 1
                        if "optional" in c["input"]:
                            option = "optional_input"
                            self.__collect_inputs(provider_name, c["input"]["optional"], option, result, "")
            return self.__shape_dataframe(pd.DataFrame(result))
        elif view == "html":
            connectors = []
            for provider_name in provider_names:
                connector = self.__config.lookup_provider(provider_name)
                if connector:
                    connectors.append(self.__transform_provider_to_connector(connector))
                else:
                    print("Unknown connector: " + provider_name, file=sys.stderr)
            return self.__render_connectors(connectors, [])
        else:
            raise RuntimeError("View must be dataframe or html.")

    # Manta's table_providers/match_given_input and
    # table_providers/latest return quite different JSON data.  This
    # method returns the format returned by the latter into the one
    # returned by the former, so we can share the HTML rendering code
    # between search(view="html") and product_inputs(view="html")
    def __transform_provider_to_connector(self, provider):
        required_input_name_sets = []
        if type(provider["version"]) is dict:
            version = provider["version"]
            for data in version["schema"]:
                for variant in data["input"]["required"]:
                    name_set = [input["name"] for input in variant]
                    required_input_name_sets.append(name_set)
        provider_name = provider.get("name") or ""
        data_source = provider.get("aegean_data_source")
        if data_source:
            data_source_name = data_source.get("name") or provider_name
        else:
            data_source_name = provider_name
        return {
            "required_input_name_sets": required_input_name_sets,
            "data_source_logo_url": provider.get("logo") or "",
            "data_source_name": data_source_name,
            "name": provider_name,
            "description": provider.get("description") or "",
            }

    def __collect_inputs(self, provider_name, req_inputs, option, result, name_prefix):
        for input in req_inputs:
            name = name_prefix + (input.get("name") or "unknown")
            type = input.get("type") or "unknown"
            description = input.get("description") or ""
            result.append(self.__make_row(provider_name, name, option, type, description))
            if (type == "Dictionary"):
                self.__collect_inputs(input["children"], option, result, name + ".")
            elif (type == "List"):
                self.__collect_inputs(input["children"], option, result, name + "[].")

    def product_outputs(self, provider_names=[], all_products=False):
        if all_products:
            provider_names = self.__config.all_provider_names()
        result = []
        for provider_name in provider_names:
            catalog = self.__connectors.product_catalog(provider_name)
            if catalog:
                for c in catalog:
                    self.__collect_outputs(provider_name, c["output"], result, "")
        return self.__shape_dataframe(pd.DataFrame(result))

    def __collect_outputs(self, provider_name, outputs, result, name_prefix):
        for o in outputs:
            name = name_prefix + (o.get("name") or "unknown")
            type = o.get("type") or "unknown"
            description = o.get("description") or ""
            result.append(self.__make_row(provider_name, name, "output", type, description))
            if (type == "Dictionary"):
                self.__collect_outputs(provider_name, o["children"], result, name + ".")
            elif (type == "List"):
                self.__collect_outputs(provider_name, o["children"], result, name + "[].")

    def __make_row(self, provider_name, attribute, option, type, description):
        return { "provider_name": provider_name,
                 "attribute": attribute,
                 "option": option,
                 "type": type,
                 "description": description }

    def __shape_dataframe(self, df):
        if len(df) > 0:
            return df[["provider_name", "attribute", "option", "type", "description"]]
        else:
            return df

    def __stringify_dframe(self, df):
        return df.astype("str")

    # Returns a DF containing information about all attributes
    # whose name includes a string.
    def attribute_search(self, name=""):
        print("Searching...")
        providers = self.__config.all_providers()
        results = []
        for p in providers:
            provider_name = p["name"]
            outputs = self.product_outputs([provider_name])
            if (len(outputs) > 0):
                matching = outputs[outputs["attribute"].str.contains(name)]
                for i, row in matching.iterrows():
                    results.append({ "provider": provider_name, "attribute": row["attribute"] })
        return pd.DataFrame(results)

    def load_input(self, csv_path_or_df):
        t = TypeGuesser(csv_path_or_df)
        t.analyze()
        return(t.data.astype(str))

    def sample_enrich(self, csv_path_or_df):
        def headline(string):
            display(HTML("<h1>" +  string + "</h1>"))
        headline("Inferring types...")
        typed_df = self.load_input(csv_path_or_df)
        display(typed_df)
        headline("Searching matching providers...")
        display(self.search(typed_df, strict=True))
        providers = self.search(typed_df, strict=True, notebook=False)
        provider_names = [p["name"] for p in providers]
        headline("Running sample enrichment...")
        return self.enrich_and_download(provider_names, typed_df.head(30), validate=False)

    # Return end of trial period as string, or None if no trial
    def __trial_period_end(self):
        headers = { "Accept": "application/json" }
        resp_json = self.__config.auth_get(self.__config.get("MANTA_URL") + "organization.json", headers=headers).json()
        trial_info = resp_json["trial_period"]
        if trial_info:
            end_date = trial_info["end_date"]
            return end_date[:10]
        else:
            return None

    def __print_startup_trial_message(self):
        end_date = self.__trial_period_end()
        if end_date:
            print("Your trial period ends on " + end_date + ". Contact client@demystdata.com to get started.")

    def __print_credits_trial_message(self, balance):
        end_date = self.__trial_period_end()
        if end_date:
            print("You have " + str(balance) + " credits left till " + end_date + ". Contact client@demystdata.com to get started.")
        else:
            print("You have " + str(balance) + " credits.")

    def sample_data(self, provider_name, row_limit=None, filters=None):
        provider = self.__config.lookup_provider(provider_name)
        if not provider:
            raise RuntimeError("Provider not found: " + provider_name)
        if not provider.get("sample_data_preview"):
            raise RuntimeError("Provider doesn't have any sample data.")
        id = str(provider["id"])
        resp = self.__config.auth_post(self.__config.get("MANTA_URL") + "table_providers/"+id+"/download_sample_data")
        df = pd.read_csv(resp.json()["url"], na_filter=False)
        if filters:
            for col_name, col_value in filters.items():
                df = df.loc[df[col_name] == col_value]
        if row_limit:
            df = df.head(row_limit)
        return df

    def report(self, enriched):
        input_cols = [c for c in enriched.columns if c.startswith("inputs.")]
        output_cols = [c for c in enriched.columns if not c.startswith("inputs.")]
        return report(enriched[input_cols], enriched[output_cols])

def show_package_versions():
    installed_packages = pkg_resources.working_set
    for i in installed_packages:
        print("%s==%s" % (i.key, i.version))
