from rest_framework.relations import ManyRelatedField
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.utils.module_loading import import_string

from .expandable import ExpandableMixin
from ..utils import (
    get_object,
    get_class_name,
    get_path_parts,
    DictDiffer,
    HashableList,
    HashableDict,
)


# TODO: Add an assertion for field names existing on the model.
# TODO: Detect and fallback to default representation for circular references instead of
# just removing the field completely on the parent.


class ExpandableRelatedFieldMixin(ExpandableMixin):
    settings_attr = "expand_settings"
    initialized_attrs = ["allowed", "ignored"]
    comparison_field_name = "uuid"

    def __init__(self, *args, **kwargs):
        for name in self.initialized_attrs:
            kwarg = kwargs.pop(name, None)
            if kwarg is not None:
                setattr(self, name, kwarg)

        super().__init__(*args, **kwargs)

    @property
    def settings(self):
        """
        Returns the settings used for this related field instance.
        """
        return getattr(self, self.settings_attr, {})

    @property
    def ignored_paths(self):
        """
        Returns a list of field paths to ignore when generating the representation of
        this field instance.
        """
        ignored_paths = []
        ignored = getattr(self, "ignored", None)

        if ignored is not None:
            for path in ignored:
                ignored_paths.append(self.get_field_path(path))

        return ignored_paths

    def is_ignored(self, path):
        """
        Returns True/False if the specified path is one of the ignored field paths. Used
        by to_representation_for_field to determine if the field is the one to expand.
        """
        if path in self.ignored_paths:
            return True

        return False

    def to_non_circular_path(self, path):
        if self.is_circular(path):
            try:
                prefix, field_name = path.rsplit(".", 1)
                return prefix
            except ValueError:
                return path
        return path

    def is_circular(self, path):
        try:
            prefix, field_name = path.rsplit(".", 1)
        except ValueError:
            field_name = path

        if field_name in self.circular_field_names:
            return True
        return False

    @property
    def circular_field_names(self):
        circular_field_names = []

        # Remove circular references to the parent model.
        parent_model_name = self.model_serializer.get_model_name()
        parent_set_name = "{}_set".format(parent_model_name)
        parent_names = (parent_model_name, parent_set_name)
        for parent_name in parent_names:
            circular_field_names.append(parent_name)

        return circular_field_names

    def get_skipped_fields(self, skipped=None):
        """
        Returns a list of field paths (ignored and skipped) to pass to the serializer
        class so it doensn't return them in the representation.
        """
        skipped_fields = self.ignored_paths

        for field_name in self.circular_field_names:
            skipped_fields.append(field_name)

        if skipped is not None:
            skipped_fields.extend(skipped)

        return list(set(skipped_fields))

    @property
    def allowed_paths(self):
        """
        Returns a list of field paths that are permitted to be expanded from this
        expandable class instance.
        """
        allowed = getattr(self, "allowed", [])
        allowed_paths = [self.get_field_path(x) for x in allowed]
        return allowed_paths

    def is_allowed(self, path):
        """
        Returns True/False if the specified path is one of the allowed field paths. Used
        by to_representation_for_field to determine if the field is to be expanded.
        """
        if path.startswith(self.allowed_prefix):
            return True
        if path in self.allowed_paths:
            return True
        return False

    def assert_is_allowed(self, path):
        """
        Raises an AssertionError if the field path specified is not in the list of
        allowed field paths.
        """
        model_serializer_name = get_class_name(self.model_serializer)
        model_serializer_field_name = self.model_serializer_field_name
        related_field_class_name = get_class_name(self)
        if self.is_allowed(path) is False:

            path = ".".join(path.split(".")[1:])

            raise AssertionError(
                "The path '{}' is not listed as an allowed field path on {}'s {} "
                "field. Please add the path to 'allowed' kwarg on {}'s '{}' field "
                "to allow its expansion.".format(
                    path,
                    model_serializer_name,
                    model_serializer_field_name,
                    model_serializer_name,
                    model_serializer_field_name,
                )
            )

    def assert_is_specified(self, path):
        """
        Raises an AssertionError if the field path specified is not in the list of
        entries in the 'expands' attribute on the related field class instance.
        """
        if self.is_specified(path) is False:
            # if field_path.startswith(self.model_name):
            #    field_path.replace("{}.".format(self.model_name), "")
            msg = []
            indent = "\n"
            for d in self.settings.get("serializers", []):
                msg.append(
                    "{}{}{}".format(d["serializer"], indent, indent.join(d["paths"]))
                )

            raise AssertionError(
                "The field path '{field_path}' is not specified in '{attr_name}' on "
                "{related_field_class_name}.\n\nCurrently Specified:\n{specified}".format(
                    field_path=path,
                    attr_name=self.settings_attr,
                    related_field_class_name=get_class_name(self),
                    specified="\n".join(msg),
                )
            )

    def is_specified(self, path):
        """
        Returns True/False if the specified path is in any of the listed paths  on the
        class isntance's 'expands' attribute.
        """
        for d in self.settings.get("serializers", []):
            if path in d.get("paths", []):
                return True
        return False

    def is_matching(self, requested_path):
        """
        Returns True/False if the requested path starts with the current
        'model_serializer_field_name'.
        """
        base_path = self.get_field_path(self.model_serializer_field_name)
        if requested_path == base_path:
            return True

        prefix = "{}.".format(base_path)
        if requested_path.startswith(prefix):
            return True

        return False

    def to_default_representation(self, obj):
        """
        Returns the default representation of the object.
        """
        return super().to_representation(obj)

    def expand_object(self, obj, path):
        """
        Method for expanding a model instance object. If a target field name is
        specified, the serializer will use that nested object to generate a
        representation.
        """
        # If the field exists, but its an empty object (no entry saved), obj will be
        # None. So, if we get None as obj, return None instead of trying to serializer
        # its representation.
        if obj is None:
            return None

        serializer = self.get_serializer(obj, path)
        representation = serializer.to_representation(obj)

        return representation

    def get_alias(self, prefix_field, prefix_path, suffix_field, suffix_path):
        for d in self.settings.get("aliases", []):
            if prefix_path in d.get("paths", []):
                alias = d.get("alias", {})
                prefix_field = alias.get("prefix_field", prefix_field)
                prefix_path = alias.get("prefix_path", prefix_path)
                suffix_field = alias.get("suffix_field", suffix_field)
                suffix_path = alias.get("suffix_path", suffix_path)
        return (prefix_field, prefix_path, suffix_field, suffix_path)

    def expand(self, obj, prefix_field, prefix_path, suffix_field, suffix_path):
        if isinstance(obj, Manager):
            obj = obj.all()

        target = obj
        target_name = get_class_name(get_object(target)).lower()
        names = (target_name, "{}_set".format(target_name))

        if len(prefix_field) and prefix_field not in names:
            target = getattr(target, prefix_field, target)

        expanded = self.expand_object(target, prefix_path)

        if len(suffix_field):
            # If our prefix path is a manytomanyfield, then use the first string in the
            # suffix path as the field name.
            if prefix_path.endswith("_set"):
                try:
                    suffix_field, _ = suffix_path.split(".", 1)
                except ValueError:
                    suffix_field = suffix_path
            expanded[suffix_field] = self.get_expanded(target, suffix_path)

        return expanded

    def get_expanded(self, obj, path):
        """
        Fascade method for expanding objects or querysets into expanded (nested)
        representations.
        """
        prefix_field, prefix_path, suffix_field, suffix_path = get_path_parts(obj, path)
        prefix_field, prefix_path, suffix_field, suffix_path = self.get_alias(
            prefix_field, prefix_path, suffix_field, suffix_path
        )
        if isinstance(obj, QuerySet):
            return [self.get_expanded(o, path) for o in obj]

        return self.expand(obj, prefix_field, prefix_path, suffix_field, suffix_path)

    def has_comparison_field(self, d1, d2):
        """
        Returns True/False if both 'd1' and 'd2' have the 'comparison_field' key,
        regardless of their respective values.
        """
        result = False
        for name in self.settings.get("comparison_fields", []):
            if result is True:
                break
            result = all([name in x for x in [d1, d2]])
        return result

    def compare_objects(self, d1, d2):
        for name in self.settings.get("comparison_fields", []):
            if all([name in x for x in [d1, d2]]):
                return d1[name] == d2[name]
        return False

    def get_changed_field_names(self, d1, d2):
        return DictDiffer(d1, d2).changed()

    def get_target_field_names(self, paths):
        result = []
        for path in paths:
            bits = path.split(".")
            field_name = bits[-1]
            try:
                i = bits.index(field_name)
                if bits[i - 2].endswith("_set"):
                    field_name = bits[i - 1]
            except IndexError:
                pass
            result.append(field_name)
        return result

    def to_expanded_representation(self, obj, paths):
        """
        Entry method for converting an model object instance into a representation by
        expanding the paths specified (if they are allowed and specified).
        """
        if isinstance(obj, Manager):
            obj = obj.all()

        expanded = None
        target_fields = self.get_target_field_names(paths)

        if len(paths) > 1:
            # expand multiple fields
            for path in paths:
                current = self.get_expanded(obj, path)

                if expanded is None:
                    expanded = current
                elif isinstance(expanded, list):
                    for d1 in expanded:
                        for d2 in current:
                            if self.has_comparison_field(d1, d2):
                                if self.compare_objects(d1, d2):
                                    changed_fields = self.get_changed_field_names(
                                        d1, d2
                                    )
                                    for field_name in changed_fields:
                                        # The dict with the updated (from a url) will
                                        # have a smaller length.
                                        if len(d2[field_name]) < len(d1[field_name]):
                                            d1[field_name] = d2[field_name]
        else:
            # expand single field
            expanded = self.get_expanded(obj, paths[0])

        if isinstance(expanded, list):
            return HashableList(expanded)
        return HashableDict(expanded)

    def get_serializer_context(self):
        return self.context

    def get_serializer(self, source, path=None, context=None):
        """
        Finds and returns the serializer class instance to use. Either imports the class
        specified in the entry on the 'expands' attribute of the ExpandableRelatedField
        instance, or re-uses the serializer class that was already imported and saved to
        the settings previously.
        """
        serializer_class = None

        if context is None:
            context = self.context

        ret = {"skipped_fields": [], "many": False, "context": context}

        if isinstance(source, Manager):
            source = source.all()

        if isinstance(source, (ManyRelatedField, QuerySet)):
            ret["many"] = True

        for d in self.settings.get("serializers", []):
            if path in d.get("paths", []):
                serializer_class = self.get_serializer_class(d["serializer"])
                ret["skipped_fields"] = self.get_skipped_fields(d.get("skipped", []))
                ret["many"] = d.get("many", ret["many"])

        if not isinstance(source, QuerySet):
            ret["many"] = False
        # if ret["many"] is True:
        #    if not isinstance(source, (QuerySet)):
        #        source = QuerySet(source)

        if serializer_class is None:
            raise RuntimeError(
                "There is no specification for '{path}' in {class_name}.\n\n"
                "Add a dictionary to the 'expandable' list with:\n"
                "    'paths': ['{path}']".format(
                    path=path, class_name=get_class_name(self)
                )
            )

        # print("---------- get_serializer_class -----------")
        # print("path: ", path)
        # print("serializer_class: ", serializer_class.__name__)
        return serializer_class(**ret)

    def get_serializer_class(self, serializer_path):
        """
        Returns the serializer class to use for serializing the object instances.
        """
        target = None

        for d in self.settings.get("serializers", []):
            if serializer_path == d.get("serializer", ""):
                target = d

        if target is None:
            raise AttributeError(
                "Failed to find an entry for serializer '{}'.".format(serializer_path)
            )

        klass = target.get("serializer_class", None)
        if klass is None:
            klass = target["serializer_class"] = import_string(serializer_path)

        return klass
