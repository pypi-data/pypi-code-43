import mwklient.listing
import mwklient.errors


class Mixin:

    def extlinks(self):
        """List external links from the current page.

        API doc: https://www.mediawiki.org/wiki/API:Extlinks

        """
        return mwklient.listing.PageProperty(
            self, 'extlinks', 'el', return_values='*')

    def iwlinks(self):
        """List interwiki links from the current page.

        API doc: https://www.mediawiki.org/wiki/API:Iwlinks

        """
        return mwklient.listing.PageProperty(
            self, 'iwlinks', 'iw', return_values=('prefix', '*'))

    def langlinks(self, **kwargs):
        """List interlanguage links from the current page.

        API doc: https://www.mediawiki.org/wiki/API:Langlinks

        """
        return mwklient.listing.PageProperty(
            self, 'langlinks', 'll', return_values=('lang', '*'), **kwargs)

    def links(self, namespace=None, generator=True, redirects=False):
        """List links to other pages from the current page.

        API doc: https://www.mediawiki.org/wiki/API:Links

        """
        prefix = mwklient.listing.List.get_prefix('pl', generator)
        kwargs = dict(
            mwklient.listing.List.generate_kwargs(prefix, namespace=namespace))

        if redirects:
            kwargs['redirects'] = '1'
        if generator:
            return mwklient.listing.PagePropertyGenerator(
                self, 'links', 'pl', **kwargs)
        return mwklient.listing.PageProperty(self, 'links', 'pl',
                                             return_values='title', **kwargs)

    # Properties
    def backlinks(self,
                  namespace=None,
                  filterredir='all',
                  redirect=False,
                  limit=None,
                  generator=True):
        """List pages that link to the current page, similar to
        Special:Whatlinkshere.

        API doc: https://www.mediawiki.org/wiki/API:Backlinks

        """
        prefix = mwklient.listing.List.get_prefix('bl', generator)
        kwargs = dict(
            mwklient.listing.List.generate_kwargs(
                prefix,
                namespace=namespace,
                filterredir=filterredir,
            ))
        if redirect:
            kwargs['%sredirect' % prefix] = '1'
        kwargs[prefix + 'title'] = self.name

        return mwklient.listing.List.get_list(generator)(
            self.site,
            'backlinks',
            'bl',
            limit=limit,
            return_values='title',
            **kwargs)
