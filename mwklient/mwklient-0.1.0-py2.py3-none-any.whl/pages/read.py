import time
from six import text_type
import mwklient.listing
import mwklient.errors


class Mixin:

    def text(self,
             section=None,
             expandtemplates=False,
             cache=True,
             slot='main'):
        """Get the current wikitext of the page, or of a specific section.

        If the page does not exist, an empty string is returned. By
        default, results will be cached and if you call text() again
        with the same section and expandtemplates the result will come
        from the cache. The cache is stored on the instance, so it
        lives as long as the instance does.

        Args:
            section (int): numbered section or `None` to get the whole page
            (default: `None`)
            expandtemplates (bool): set to `True` to expand templates
            (default: `False`)
            cache (bool): set to `False` to disable caching (default: `True`)
        """

        if self.cannot('read'):
            raise mwklient.errors.InsufficientPermission(self)
        if not self.exists:
            return u''
        if section is not None:  # can be 0
            section = text_type(section)

        key = hash((section, expandtemplates))
        if cache and key in self._textcache:
            return self._textcache[key]

        revs = self.revisions(
            prop='content|timestamp', limit=1, section=section, slots=slot)
        try:
            rev = next(revs)
            if 'slots' in rev:
                text = rev['slots'][slot]['*']
            else:
                text = rev['*']
            self.last_rev_time = rev['timestamp']
        except StopIteration:
            text = u''
            self.last_rev_time = None
        if not expandtemplates:
            self.edit_time = time.gmtime()
        else:
            # The 'rvexpandtemplates' option was removed in MediaWiki 1.32, so
            # we have to make an extra API call.
            # See: https://github.com/mwclient/mwclient/issues/214
            text = self.site.expandtemplates(text)

        if cache:
            self._textcache[key] = text
        return text

    def categories(self, generator=True, show=None):
        """List categories used on the current page.

        API doc: https://www.mediawiki.org/wiki/API:Categories

        Args:
            generator (bool): Return generator (Default: True)
            show (str): Set to 'hidden' to only return hidden categories
                or '!hidden' to only return non-hidden ones.

        Returns:
            mwklient.listings.PagePropertyGenerator
        """
        prefix = mwklient.listing.List.get_prefix('cl', generator)
        kwargs = dict(mwklient.listing.List.generate_kwargs(prefix, show=show))

        if generator:
            return mwklient.listing.PagePropertyGenerator(
                self, 'categories', 'cl', **kwargs)
        # TODO: return sortkey if wanted
        return mwklient.listing.PageProperty(
            self, 'categories', 'cl', return_values='title', **kwargs)

    def embeddedin(self,
                   namespace=None,
                   filterredir='all',
                   limit=None,
                   generator=True):
        """List pages that transclude the current page.

        API doc: https://www.mediawiki.org/wiki/API:Embeddedin

        Args:
            namespace (int): Restricts search to a given namespace
            (Default: None)
            filterredir (str): How to filter redirects, either 'all' (default),
                'redirects' or 'nonredirects'.
            limit (int): Maximum amount of pages to return per request
            generator (bool): Return generator (Default: True)

        Returns:
            mwklient.listings.List: Page iterator
        """
        prefix = mwklient.listing.List.get_prefix('ei', generator)
        kwargs = dict(
            mwklient.listing.List.generate_kwargs(
                prefix, namespace=namespace, filterredir=filterredir))
        kwargs[prefix + 'title'] = self.name

        return mwklient.listing.List.get_list(generator)(
            self.site,
            'embeddedin',
            'ei',
            limit=limit,
            return_values='title',
            **kwargs)

    def images(self, generator=True):
        """List files/images embedded in the current page.

        API doc: https://www.mediawiki.org/wiki/API:Images

        """
        if generator:
            return mwklient.listing.PagePropertyGenerator(self, 'images', '')
        return mwklient.listing.PageProperty(self, 'images', '',
                                             return_values='title')

    def templates(self, namespace=None, generator=True):
        """List templates used on the current page.

        API doc: https://www.mediawiki.org/wiki/API:Templates

        """
        prefix = mwklient.listing.List.get_prefix('tl', generator)
        kwargs = dict(
            mwklient.listing.List.generate_kwargs(prefix, namespace=namespace))
        if generator:
            return mwklient.listing.PagePropertyGenerator(
                self, 'templates', prefix, **kwargs)
        return mwklient.listing.PageProperty(self, 'templates', prefix,
                                             return_values='title', **kwargs)
