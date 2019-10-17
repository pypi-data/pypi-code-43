from ..utils import sort_field_paths


class ExpandableMixin(object):
    model_name = None
    query_param = "expand"
    expanded_fields = None

    @property
    def request(self):
        """
        Returns the current request context passed from DRF.
        """
        context = getattr(self, "context", None)
        if context is None:
            raise AttributeError("Context not found.")

        request = context.get("request", None)
        if request is None:
            raise AttributeError("Request not found in context.")

        return request

    @property
    def params(self):
        """
        Returns a list of unique relative field paths that should be used for expanding.
        """
        field_paths = []

        attr_name = getattr(self, "query_param", None)
        if attr_name is not None:
            query_params = getattr(self.request, "query_params", {})
            query_params = query_params.get(attr_name, "").split(",")
            for param in query_params:
                field_paths.append(param)

        return sort_field_paths(field_paths)

    def get_model_name(self):
        """
        Returns the model name from the ModelSerializer Meta class model specified, or
        from the previously saved model name on the class.
        """
        model_name = getattr(self, "model_name", None)

        if model_name is None:
            model = self.Meta.model
            model_name = model.__name__.lower()
            self.model_name = model_name

        return model_name

    def get_field_path(self, path):
        """
        Returns a list of possible field paths that are prefixed with the current
        serializers model name, plus one suffixed with _set for django's default
        reverse relationship names.
        """
        model_name = self.get_model_name()
        prefix = "{}.".format(model_name)
        if not path.startswith(prefix):
            return "{}{}".format(prefix, path)
        return path

    @property
    def requested_fields(self):
        """
        Returns a list of field paths to expand.
        Can be specified via class instance or via query params.
        """
        requested_fields = self.params

        # Add our target fields that we specified on the class.
        if isinstance(self.expanded_fields, list):
            for field_path in self.expanded_fields:
                requested_fields.append(field_path)

        requested_fields = sort_field_paths(requested_fields)
        return requested_fields
