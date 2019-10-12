
import mwklient.listing
import mwklient.errors


class Mixin:
    def move(self, new_title, reason='', move_talk=True, no_redirect=False):
        """Move (rename) page to new_title.

        If user account is an administrator, specify no_redirect as True to not
        leave a redirect.

        If user does not have permission to move page, an
        InsufficientPermission exception is raised.

        """
        if self.cannot('move'):
            raise mwklient.errors.InsufficientPermission(self)

        if not self.site.writeapi:
            raise mwklient.errors.NoWriteApi(self)

        data = {}
        if move_talk:
            data['movetalk'] = '1'
        if no_redirect:
            data['noredirect'] = '1'
        result = self.site.post(
            'move', ('from', self.name),
            to=new_title,
            token=self.__get_token__('move'),
            reason=reason,
            **data)
        return result['move']

    def delete(self, reason='', watch=False, unwatch=False, oldimage=False):
        """Delete page.

        If user does not have permission to delete page, an
        InsufficientPermission exception is raised.

        """
        if self.cannot('delete'):
            raise mwklient.errors.InsufficientPermission(self)

        if not self.site.writeapi:
            raise mwklient.errors.NoWriteApi(self)

        data = {}
        if watch:
            data['watch'] = '1'
        if unwatch:
            data['unwatch'] = '1'
        if oldimage:
            data['oldimage'] = oldimage
        result = self.site.post(
            'delete',
            title=self.name,
            token=self.__get_token__('delete'),
            reason=reason,
            **data)
        return result['delete']
