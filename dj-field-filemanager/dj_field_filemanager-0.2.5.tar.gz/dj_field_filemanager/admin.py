from django import forms

from . import __version__, settings
from .models import DocumentModel
from .widgets import FieldFilemanagerWidget


class FieldFilemanagerAdmin:
    FIELD_FILEMANAGER_CSS = [
        'field-filemanager/field-filemanager-%s/filemanager.css' % __version__,
        'field-filemanager/field-filemanager-%s.css' % __version__,
        ]
    FIELD_FILEMANAGER_JS = [
        'field-filemanager/field-filemanager-%s/filemanager.umd.min.js' % __version__,
        'field-filemanager/field-filemanager-%s-init.js' % __version__,
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attach_filemanager_fields()

    def attach_filemanager_fields(self):
        """
        Search DocumentModel childs and attach each widget
        """
        self.filemanager_fields = []

        for related_object in self.model._meta.related_objects:
            related_model = related_object.related_model
            if issubclass(related_model, DocumentModel):
                short_description = related_model._meta.verbose_name_plural
                model = '%s.%s' % (related_model._meta.app_label, related_model._meta.object_name)
                filemanager_field = 'filemanager_%s' % model.replace('.', '_').lower()
                parent = related_model.document_parent

                def documents(obj):
                    content = 'To add documents, save first'
                    if obj and obj.pk:
                        documents_input = FieldFilemanagerWidget(
                            attrs={'model': model, 'parent': parent, 'parent_pk': obj.pk})
                        content = documents_input.render(short_description, '')
                    return content
                documents.allow_tags = True
                documents.short_description = related_model._meta.verbose_name_plural
                documents.__name__ = filemanager_field

                setattr(self, filemanager_field, documents)
                self.filemanager_fields.append(filemanager_field)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.extend(self.filemanager_fields)
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        for field in self.filemanager_fields:
            if field not in fields:
                fields.append(field)
        return fields

    @property
    def media(self):
        css = super().media._css
        if 'all' not in css:
            css['all'] = []
        css['all'].extend(self.FIELD_FILEMANAGER_CSS)
        js = super().media._js
        if settings.FIELD_FILEMANAGER_USE_VUE_JS:
            js.append('field-filemanager/vue-2.6.10.min.js')
        js += self.FIELD_FILEMANAGER_JS
        return forms.Media(css=css, js=js)
