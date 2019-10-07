"""
Generic change log document chain.

: `parent_config`
    The manage config class for the related document.

: `parent_field`
    The field against related documents that relates them to the document.

: `parent_projection`
    The projection used when fetching the parent document.

: `projection`
    The projection used when requesting the document from the database (defaults
    to None which means the detault projection for the frame class will be
    used).

: `orphans`
    The maximum number of orphan that can be merged into the last page of
    results (the orphans will form the last page) (defaults to 2).

: `per_page`
    The number of results that will appear per page (defaults to 30).

"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm, fields
from manhattan.nav import Nav, NavItem

from manhattan.manage.views import factories, utils
from manhattan.manage.views.related import factories as related_factories
from manhattan.manage.views.change_log import change_log_chains

__all__ = ['change_log_chains']


class ListForm(BaseForm):

    _info = {}

    page = fields.IntegerField('Page', default=1)


# Define the chains
change_log_chains = change_log_chains.copy()
change_log_chains.insert_link(
    'get_document',
    'get_parent_document',
    after=True
)


# Factory overrides
change_log_chains.set_link(
    factories.config(
        form_cls=ListForm,
        parent_config=None,
        parent_field=None,
        parent_projection=None,
        projection=None,
        orphans=2,
        per_page=20
    )
)
change_log_chains.set_link(related_factories.get_parent_document())
change_log_chains.set_link(related_factories.decorate('change_log'))
