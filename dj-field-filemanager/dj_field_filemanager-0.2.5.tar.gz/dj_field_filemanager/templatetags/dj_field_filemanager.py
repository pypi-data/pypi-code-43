from django import template

from dj_field_filemanager import __version__, settings

register = template.Library()


@register.inclusion_tag('dj_field_filemanager/upload_to_folder.html', takes_context=True)
def upload_to_folder(context, code):
    css = [
        'field-filemanager/field-filemanager-%s/filemanager.css' % __version__,
        'field-filemanager/field-filemanager-%s.css' % __version__,
        ]
    js = [
        'field-filemanager/field-filemanager-%s/filemanager.umd.min.js' % __version__,
        'field-filemanager/field-filemanager-%s-init.js' % __version__,
        ]
    if settings.FIELD_FILEMANAGER_USE_VUE_JS:
        js.append('field-filemanager/vue-2.5.17.min.js')

    return {
        'css': css,
        'js': js,
        'code': code
    }
