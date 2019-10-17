from djangoldp.permissions import LDPPermissions


class InboxPermissions(LDPPermissions):
    def has_permission(self, request, view):
        from djangoldp.models import Model

        if self.is_a_container(request._request.path):
            try:
                """
                If on nested field we use users permissions
                """
                obj = Model.resolve_parent(request.path)
                model = view.parent_model

                """
                If still on nested field and request is post (/users/X/inbox/) we use notification permissions
                """
                if view.parent_model != view.model and request.method == 'POST':
                    obj = None
                    model = view.model
            except:
                """
                Not on nested field we use notification permissions
                """
                obj = None
                model = view.model
        else:
            obj = Model.resolve_id(request._request.path)
            model = view.model

        perms = self.get_permissions(request.method, model)

        for perm in perms:
            if not perm.split('.')[1].split('_')[0] in self.user_permissions(request.user, model, obj):
                return False

        return True