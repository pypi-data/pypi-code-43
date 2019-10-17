from rest_framework import filters
from .spaces import get_spaces

class SpacePermissionsFilter(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    default_space_permission_map = {
        'list': None, # all members
        'create': None,
        'retrieve': None,
        'update': ['Admin', 'Owner',],
        'partial_update': ['Admin', 'Owner'],
        'destroy': ['Admin', 'Owner'],
    }

    def filter_queryset(self, request, queryset, view):
        user_id = request.user.id
        permission_map = getattr(
            view,
            'space_permission_map',
            self.default_space_permission_map
        )
        required_permissions = permission_map.get(view.action)
        space_ids = get_spaces(user_id, required_permissions)
        if getattr(view, 'space_filters', None) is None:
            raise Exception('Please define a view.space_filter. e.g.: space_filer = "space__in" or "spaces" as in: .filter(space__in=...)')

        query = {
            view.space_filter: space_ids
        }
        queryset = view.get_queryset().filter(**query)
        return queryset
