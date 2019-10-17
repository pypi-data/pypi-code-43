from django import forms
from .fields import CommaSeparatedCharField
from django.utils.module_loading import import_string
from gurutools.helpers import push_tags_to_firestore_lookup

GURU_OBJECT_MAP = {
    "note": {
        "path": "api.models.Note",
        "query": "id__in",
    }
}
from saferunner.process_runner import safely_run_processes

class BulkFormBase(forms.Form):
    object_type = forms.CharField(required=True)
    object_ids = CommaSeparatedCharField()
    objects = None

    def clean(self):
        """Make sure that the user has permission to manage all these objects"""
        super().clean()
        objects = self.get_objects()
        for obj in objects:
            has_permission = getattr(obj, 'can_manage', None)
            if has_permission is None:
                raise AssertionError('Model must implement can_manage() method.')
            if has_permission == False:
                forms.ValidationError('You do not have permission to edit all these objects')

    def get_objects(self):
        if getattr(self, 'objects', None) is not None:
            return self.objects

        data = self.cleaned_data
        object_ids = data.get('object_ids', [])
        object_type = data.get('object_type')

        config = GURU_OBJECT_MAP.get(object_type)
        data = self.cleaned_data

        items = import_string(
            config.get('path')
        ).objects.filter(
            **{config.get('query'): object_ids}
        )
        setattr(self, 'objects', items)
        return items

class ManageSharingForm(BulkFormBase):

    add_spaces = CommaSeparatedCharField()
    remove_spaces = CommaSeparatedCharField()

    def save(self, commit=True):
        data = self.cleaned_data
        objects = self.get_objects()
        updated_objects = []
        for obj in objects:

            if not obj.spaces: obj.spaces = []

            new_spaces = set(
                obj.spaces
            ).union(
                set(data.get('add_spaces', []))
            ).difference(
                set(data.get('remove_spaces', []))
            )
            obj.spaces = list(new_spaces)
            if commit:
                obj.save()
            updated_objects.append(obj)
        return updated_objects

class ManageTagsForm(BulkFormBase):
    """
    Example payload:
    {
        object_type: 'note',
        object_ids: 1,3,4
        add_tags: 'foo,bar,bus'
        remove_tags: 'baz, bum'
    }
    """

    add_tags = CommaSeparatedCharField()
    remove_tags = CommaSeparatedCharField()

    # todo: clean -> validate has access to objects

    def save(self, commit=True):
        data = self.cleaned_data
        objects = self.get_objects()
        updated_objects = []
        for obj in objects:
            if not obj.tags: obj.tags = []

            new_tags = set(
                obj.tags
            ).union(
                set(data.get('add_tags', []))
            ).difference(
                set(data.get('remove_tags', []))
            )
            obj.tags = list(new_tags)
            if commit:
                obj.save()
            updated_objects.append(obj)
        return updated_objects

    def post_process(self, request, result, pk=None, **kwargs):

        new_tags = self.cleaned_data.get('add_tags', [])
        push_tag_lookup_args = {
            "tags": new_tags,
            "practitioner_id": request.user.id,
            "spaces": []
        }

        task_list = [
            # task, args, async
            (push_tags_to_firestore_lookup, push_tag_lookup_args, False),
        ]
        safely_run_processes(
            run_id='tag_post_process',
            task_list=task_list
        )


