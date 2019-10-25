import sys
import string
from collections import OrderedDict
import json
import hashlib
import requests
import pygsheets.client
from django.utils.six.moves.urllib.parse import urlencode
from django.utils.timezone import now
from inputflow.models import Input
from . import models
from . import credentials

class Utils:
    @staticmethod
    def fetch_token_info(token):
        """
        update token user_id and username if the token belongs to the oauth client
        selected in the settings object.
        """
        settings = models.Settings.objects.filter(oauth_client=token.client).first()
        if settings is not None:
            url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}"
            url = url.format(token.access_token)
            response = requests.get(url)
            if response.status_code == 200:
                info = response.json()
                token.user_id = info['user_id']
                token.username = info['email']

    @staticmethod
    def get_spreadsheet(spreadsheet_obj):
        creds = credentials.Credentials(spreadsheet_obj.access_token)
        client = pygsheets.client.Client(creds)
        return client.open_by_url(spreadsheet_obj.url)

    @classmethod
    def get_worksheet(cls, spreadsheet_obj):
        spreadsheet = cls.get_spreadsheet(spreadsheet_obj)
        return spreadsheet.worksheets()[spreadsheet_obj.sheet_index]

    @staticmethod
    def worksheet_row_to_dict(row):
        cols = ['COL${}'.format(letter) for letter in string.ascii_uppercase]
        encode = lambda value: value.encode('utf-8') if sys.version_info.major == 2 else value
        result = OrderedDict(((col, encode(value)) for col, value in zip(cols, row) if value != ''))
        content = json.dumps(result)
        sha1 = hashlib.sha1(content.encode('utf-8'))
        result['_content_hash'] = sha1.hexdigest()
        return result

    @classmethod
    def get_worksheet_row(cls, worksheet, index):
        row = worksheet.get_row(index)
        non_empty = [col for col in row if col != '']
        row = cls.worksheet_row_to_dict(row)
        row['row'] = index
        if len(non_empty) == 0:
            return None
        return row

    @classmethod
    def iter_worksheet_rows(cls, spreadsheet_obj, max_count=100):
        available_rows = max_count
        row_index = spreadsheet_obj.last_imported_row
        if row_index is None:
            row_index = 2 if spreadsheet_obj.omit_first_row else 1
        else:
            row_index += 1
        worksheet = cls.get_worksheet(spreadsheet_obj)
        while available_rows:
            row = cls.get_worksheet_row(worksheet, row_index)
            if row is None:
                return
            row_index += 1
            available_rows -= 1
            yield row

    @classmethod
    def import_to_input_flow(cls, spreadsheet_obj):
        if spreadsheet_obj.input_settings is None:
            return
        imported = True
        count = 0
        while imported:
            imported = False
            for row in cls.iter_worksheet_rows(spreadsheet_obj):
                imported = True
                encoded_row = urlencode(row)
                input_row = Input()
                input_row.settings = spreadsheet_obj.input_settings
                input_row.internal_source = True
                input_row.format = 'form'
                input_row.raw_content = encoded_row
                input_row.save()
                spreadsheet_obj.last_imported_row = row['row']
                spreadsheet_obj.last_imported_date = now()
                spreadsheet_obj.save()
                input_row.notify()
                count += 1
        return count
