import six
from mwklient.util import parse_timestamp, strip_namespace
import mwklient.listing
import mwklient.errors
from mwklient.pages import read as READ, link as LINK
from mwklient.pages import edit as EDIT, hazard as HAZARD


class Page(READ.Mixin, EDIT.Mixin, LINK.Mixin, HAZARD.Mixin):
    def __init__(self, site, name, info=None, extra_properties=None):
        if type(name) is type(self):
            self.__dict__.update(name.__dict__)
            return
        self.site = site
        self.name = name
        self._textcache = {}

        if not info:
            if extra_properties:
                prop = 'info|' + '|'.join(six.iterkeys(extra_properties))
                extra_props = []
                for extra_prop in six.itervalues(extra_properties):
                    extra_props.extend(extra_prop)
            else:
                prop = 'info'
                extra_props = ()

            if isinstance(name, int):
                info = self.site.get(
                    'query',
                    prop=prop,
                    pageids=name,
                    inprop='protection',
                    *extra_props)
            else:
                info = self.site.get(
                    'query',
                    prop=prop,
                    titles=name,
                    inprop='protection',
                    *extra_props)
            info = six.next(six.itervalues(info['query']['pages']))
        self._info = info

        if 'invalid' in info:
            raise mwklient.errors.InvalidPageTitle(info.get('invalidreason'))

        self.namespace = info.get('ns', 0)
        self.name = info.get('title', u'')
        if self.namespace:
            self.page_title = strip_namespace(self.name)
        else:
            self.page_title = self.name

        self.touched = parse_timestamp(info.get('touched'))
        self.revision = info.get('lastrevid', 0)
        self.exists = 'missing' not in info
        self.length = info.get('length')
        self.protection = {
            i['type']: (i['level'], i['expiry'])
            for i in info.get('protection', ()) if i
        }
        self.redirect = 'redirect' in info
        self.pageid = info.get('pageid', None)
        self.contentmodel = info.get('contentmodel', None)
        self.pagelanguage = info.get('pagelanguage', None)
        self.restrictiontypes = info.get('restrictiontypes', None)

        self.last_rev_time = None
        self.edit_time = None

    def redirects_to(self):
        """ Returns the redirect target page, or None if the page is not a
        redirect page."""
        info = self.site.get(
            'query', prop='pageprops', titles=self.name, redirects='')['query']
        if 'redirects' in info:
            for page in info['redirects']:
                if page['from'] == self.name:
                    return Page(self.site, page['to'])
        return None

    def resolve_redirect(self):
        """ Returns the redirect target page, or the current page if it's not a
        redirect page."""
        target_page = self.redirects_to()
        if target_page is None:
            return self
        return target_page

    def __repr__(self):
        return "<Page object '%s' for %s>" % (self.name.encode('utf-8'),
                                              self.site)

    def __unicode__(self):
        return self.name

    def can(self, action):
        """Check if the current user has the right to carry out some action
        with the current page.

        Example:
            >>> page.can('edit')
            True

        """
        level = self.protection.get(action, (action, ))[0]
        if level == 'sysop':
            level = 'editprotected'

        return level in self.site.rights

    def cannot(self, action):
        """Check if the current user has not the right to carry out some action
        with the current page.

        Example:
            >>> page.cannot('edit')
            True

        """
        return not self.can(action)

    def __get_token__(self, type_t, force=False):
        return self.site.get_token(type_t, force, title=self.name)

    def purge(self):
        """Purge server-side cache of page. This will re-render templates and
        other dynamic content.

        """
        self.site.post('purge', titles=self.name)

    # def watch: requires 1.14

    def revisions(self,
                  startid=None,
                  endid=None,
                  start=None,
                  end=None,
                  direc='older',
                  user=None,
                  excludeuser=None,
                  limit=50,
                  prop='ids|timestamp|flags|comment|user',
                  expandtemplates=False,
                  section=None,
                  diffto=None,
                  slots=None, uselang=None):
        """List revisions of the current page.

        API doc: https://www.mediawiki.org/wiki/API:Revisions

        Args:
            startid (int): Revision ID to start listing from.
            endid (int): Revision ID to stop listing at.
            start (str): Timestamp to start listing from.
            end (str): Timestamp to end listing at.
            direc (str): Direction to list in: 'older' (default) or 'newer'.
            user (str): Only list revisions made by this user.
            excludeuser (str): Exclude revisions made by this user.
            limit (int): The maximum number of revisions to return per request.
            prop (str): Which properties to get for each revision,
                default: 'ids|timestamp|flags|comment|user'
            expandtemplates (bool): Expand templates in rvprop=content output
            section (int): If rvprop=content is set, only retrieve the contents
            of this section.
            diffto (str): Revision ID to diff each revision to. Use "prev",
                          "next" and "cur" for the previous, next and current
                          revision respectively.
            slots (str): The content slot (Mediawiki >= 1.32) to retrieve
                content from.
            uselang (str): Language to use for parsed edit comments and other
                           localized messages.

        Returns:
            mwklient.listings.List: Revision iterator
        """
        kwargs = dict(
            mwklient.listing.List.generate_kwargs(
                'rv',
                startid=startid,
                endid=endid,
                start=start,
                end=end,
                user=user,
                excludeuser=excludeuser,
                diffto=diffto,
                slots=slots))

        if self.site.version[:2] < (1, 32) and 'rvslots' in kwargs:
            # https://github.com/mwclient/mwclient/issues/199
            del kwargs['rvslots']

        kwargs['rvdir'] = direc
        kwargs['rvprop'] = prop
        kwargs['uselang'] = uselang
        if expandtemplates:
            kwargs['rvexpandtemplates'] = '1'
        if section is not None:
            kwargs['rvsection'] = section

        return mwklient.listing.RevisionsIterator(
            self, 'revisions', 'rv', limit=limit, **kwargs)
