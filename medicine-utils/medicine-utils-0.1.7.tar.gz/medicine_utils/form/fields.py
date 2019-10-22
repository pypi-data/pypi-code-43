
import xmltodict

from io import BytesIO
from lxml import etree

from django import forms


class XmlDataDictFileField(forms.FileField):

    def to_python(self, data):
        f = super().to_python(data)
        if f is None:
            return None

        if hasattr(data, 'temporary_file_path'):
            file = data
        else:
            if hasattr(data, 'read'):
                file = BytesIO(data.read())
            else:
                file = BytesIO(data['content'])

        try:
            f.tree = etree.parse(file)
            f.data = xmltodict.parse(BytesIO(etree.tostring(f.tree)))
        except etree.XMLSyntaxError:
            raise forms.ValidationError('Неправильный формат файла')

        return f
