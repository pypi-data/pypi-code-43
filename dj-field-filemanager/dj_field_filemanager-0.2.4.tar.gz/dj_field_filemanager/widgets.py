from django import forms


class FieldFilemanagerWidget(forms.Widget):
    template_name = 'dj_field_filemanager/field_filemanager_widget.html'
