from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

__all__ = ['recover_selected', 'hard_delete_selected']


def recover_selected(modeladmin, request, queryset):
    number_of_rows_recovered, __ = queryset.undelete()  # __ = recovered_items
    if number_of_rows_recovered == 1:
        message_bit = _('1 record was')
    else:
        message_bit = _('%(number_of_rows)s records were') % dict(number_of_rows=number_of_rows_recovered)
    message = _('%(message_bit)s successfully marked as active') % dict(message_bit=message_bit)
    modeladmin.message_user(request, message)


def hard_delete_selected(modeladmin, request, queryset):
    opts = modeladmin.model._meta  # # pylint: disable=W0212

    deletable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)

    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        if queryset.count():
            number_of_rows_deleted, __ = queryset.hard_delete()  # __ = deleted_items
            if number_of_rows_deleted == 1:
                message_bit = _('1 record was')
            else:
                message_bit = _('%(number_of_rows)s records were') % dict(number_of_rows=number_of_rows_deleted)
            message = _('%(message_bit)s deleted') % dict(message_bit=message_bit)
            modeladmin.message_user(request, message)
        return None

    objects_name = model_ngettext(queryset)
    if perms_needed or protected:
        title = _('Cannot delete %(name)s') % {'name': objects_name}
    else:
        title = _('Are you sure?')

    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'objects_name': str(objects_name),
        'deletable_objects': [deletable_objects],
        'model_count': dict(model_count).items(),
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    return TemplateResponse(request, 'admin/hard_delete_selected_confirmation.html', context)
