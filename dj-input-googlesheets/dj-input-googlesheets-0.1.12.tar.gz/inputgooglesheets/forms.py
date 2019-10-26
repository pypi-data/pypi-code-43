import googleapiclient.errors
import pygsheets.client
from django import forms
from django.utils.translation import ugettext
from . import models
from . import credentials


class SpreadSheetForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'access_token', 'url', 'sheet_index', 'omit_first_row',
            'automatically_imported', 'input_settings','enabled')

    def clean(self):
        cleaned_data = super(SpreadSheetForm, self).clean()
        token = cleaned_data['access_token']
        sheet_index = cleaned_data['sheet_index']
        url = cleaned_data['url']
        try:
            creds = credentials.Credentials(token)
            client = pygsheets.client.Client(creds)
            spreadsheet = client.open_by_url(url)
            sheets = spreadsheet.worksheets()
            if sheet_index >= len(sheets):
                msg = ugettext("Wrong worksheet index.")
                self.add_error('sheet_index', msg)
        except googleapiclient.errors.HttpError as e:
            msg = ugettext("Invalid spreadsheet url.")
            if e.resp and e.resp['status'] == '403':
                msg = ugettext("You have no access to this spreadsheet.")
            self.add_error('url', msg)
        except Exception:
            msg = ugettext("Invalid spreadsheet url.")
            self.add_error('url', msg)
        return cleaned_data

    def save(self, *args, **kwargs):
        creds = credentials.Credentials(self.instance.access_token)
        client = pygsheets.client.Client(creds)
        spreadsheet = client.open_by_url(self.instance.url)
        self.instance.url = spreadsheet.url
        self.instance.uid = spreadsheet.id
        self.instance.spreadsheet_name = spreadsheet.title
        sheets = spreadsheet.worksheets()
        self.instance.sheet_name = sheets[self.instance.sheet_index].title
        return super(SpreadSheetForm, self).save(*args, **kwargs)
