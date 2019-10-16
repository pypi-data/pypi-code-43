# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-simplefacet views/views for web ui"""

from logilab.mtconverter import xml_escape

from cubicweb import UnknownEid, _

from cubicweb.web import component
from cubicweb.web.views.facets import (facets,
                                       FilterBox, ETypeFacet, HasTextFacet)
from cubicweb.predicates import match_context, match_form_params
from cubicweb.web import facet as facetbase
from cubicweb.web.views.facets import FilterBox
from cubicweb.web.views.magicsearch import BaseQueryProcessor


###############################################################################
### COMPONENTS ################################################################
###############################################################################

def normalize_facetid(facetid):
    return facetid.replace('.', '-')


class SimpleFacetFilterBox(FilterBox):
    title = _('refine your search')
    _title_html = ('<button class="btn btn-link" onclick="$(\'#%s-content\').slideToggle(\'fast\')">'
                   '%s&#160;<b class="caret"></b></button>')
    _display_new_search_link = True
    bk_linkbox_template = '<p class="btn btn-small btn-facet">%s</p>'

    @property
    def start_url(self):
        facet_list = self._cw.form.get('_facet',[])
        form = self._cw.form.copy()
        if facet_list:
            form.pop('_facet')
        return self._cw.build_url(self._cw.relative_path(includeparams=False),
                                       **form)

    def render_title(self, w):
        """return the title for this component"""
        if self.title:
            w(self._cw._(self.title).capitalize())

    def generate_form(self, w, rset, divid, vid, vidargs=None, mainvar=None,
                      paginate=False, cssclass='', hiddens=None, **kwargs):
        kwargs.pop('context', None)
        baserql, wdgs = facets(self._cw, rset, context=self.__regid__,
                                   mainvar=mainvar, **kwargs)
        self.layout_widgets(w, self.sorted_widgets(wdgs))

    def layout_widgets(self, w, wdgs):
        self._cw.add_js('cubes.simplefacet.js')
        self._cw.add_css('cubes.simplefacet.css')
        w('<div class="facetgroup">')
        facet_list = self._cw.form.get('_facet',[])
        start_url = self.start_url
        if self._display_new_search_link :
            w('&#160;<a href="%(url)s" title="%(title)s" class="remove-all-filters">%(title)s</a>' \
          % {'url':start_url, 'title':self._cw._('new search')})
        if isinstance(facet_list, str):
            facet_list = (facet_list,)
        facet_ids = set(f.split(':', 2)[0] for f in facet_list)
        for wdg in wdgs:
            title_class = ''
            facet = wdg.facet
            # if hasattr(facet, 'icon'):
            #     icon = facet.icon
            # else:
            #     icon = 'icon-resize-small'
            if facet.__regid__ in list(facet_ids):
                facet.start_unfolded = True
                title_class = ' selected'
            self.display_facet_title(w, facet, title_class)
            unfolded = 'style="display: block;"' if facet.start_unfolded else ''
            w('<div id="%s-content" class="facet-content" %s>'
              % (normalize_facetid(facet.__regid__), unfolded))
            wdg.render(w=w)
            w('</div>')
        w('</div>') # facetgroup

    def display_facet_title(self, w, facet, title_class):
        if not hasattr(facet, 'no_title'):
            w('<div class="facet-title%s">' % title_class)
            w(self._title_html % (normalize_facetid(facet.__regid__), self._cw._(facet.title)))
            w('</div>')

    def focus_link(self, rset):
        # override default focus_link: we simply don't want it
        return ''

class PageTopLayout(component.Layout):
    __select__ =  match_context('top')

    def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            view.render_body(w)

class AppliedFacetsComponent(component.CtxComponent):
    __regid__ = 'applied-facets'
    __select__ = component.CtxComponent.__select__ & match_form_params('_facet')

    contextual = True
    _title_html = ('<h3 class="boxTitle"><b>%s</b>'
                   '<a href="%s" class="remove-all-filters">&#160;x</a></h3>')
    _li_html = ('<li class="facetitem"><a href="%s" rel="tooltip" data-placement="right" data-original-title="%s" class="facet-unapply">'
                '%s&#160;<span>x</span></a></li>')
    _filter_box_html = ('<div class="applied-filter">'
                        '<div class="applied-filter-title">%s</div>'
                        '<ul class="facet-values">%s</ul></div>')
    context = 'navcontenttop'
    style = 'badges'
    display_title = False

    def render_body(self, w):
        if self.style == 'badges':
            self.render_component_as_badges(w)
        else:
            self.render_component_as_box(w)

    def render_component_as_box(self, w):
        form = self._cw.form
        facet_list = self._cw.form['_facet']
        if isinstance(facet_list, str):
            facet_list = (facet_list,)
        w('<div id="facet_filter">')
        form2 = form.copy()
        form2.pop('_facet')
        start_url = self.start_url(**form2)
        if self.display_title:
            w(self._title_html % (xml_escape(self._cw._('currently applied filters')), start_url))
        facet_dico = {}
        facet_ids = {}
        select = self._cw.vreg.parse(self._cw,  form['_original_rql_']).children[0]
        filtered_variable = select.selection[0].variable
        for facetinfo in facet_list:
            facetid, facetvalue = facetinfo.split(':')
            facet = facetbase.get_facet(self._cw, facetid, select, filtered_variable)
            if facetid not in facet_ids:
                facet_ids[facetid] = self._cw._(facet.title)
            if not facetvalue:
                value_label = self._cw._(facet.no_relation_label)
            elif isinstance(facet, HasTextFacet):
                value_label = facetvalue
            elif isinstance(facet, ETypeFacet):
                value_label = self._cw._(facetvalue)
            else:
                try:
                    entity = self._cw.entity_from_eid(facetvalue)
                    attr = getattr(facet, 'target_attr', None)
                    if getattr(facet, 'display_dc_title', None) or not attr:
                        value_label = entity.dc_title()
                    else:
                        value_label = getattr(entity, attr)
                except UnknownEid:
                    value_label = self._cw._(facet.no_relation_label)
                except ValueError:
                    value_label = facetvalue
            all_but_this_facet = list(facet_list) # copy + list conversion
            all_but_this_facet.remove(facetinfo)
            new_url = self.compute_remove_url(all_but_this_facet, facet_list, form2)
            facet_dico.setdefault(facetid, []).append((value_label, new_url))
        for facetid, values in facet_dico.items():
            html = ''.join(self._li_html  % (new_url, xml_escape(self._cw._('remove this filter')), label)
                            for label, new_url in values)
            w(self._filter_box_html % (facet_ids[facetid], html))
        w('</div>')

    def render_component_as_badges(self, w):
        facet_list = self._cw.form['_facet']
        if isinstance(facet_list, str):
            facet_list = (facet_list,)
        form2 = self._cw.form.copy()
        form2.pop('_facet')
        start_url = self.start_url(**form2)
        w('<div id="facet-filter">')
        facet_dico = {}
        facet_ids = {}
        form = self._cw.form
        select = self._cw.vreg.parse(self._cw,  form['_original_rql_']).children[0]
        filtered_variable = select.selection[0].variable
        for facetinfo in facet_list:
            facetid, facetvalue = facetinfo.split(':')
            facet = facetbase.get_facet(self._cw, facetid, select, filtered_variable)
            if facetid not in facet_ids:
                facet_ids[facetid] = self._cw._(facet.title)
            if not facetvalue:
                value_label = self._cw._(facet.no_relation_label)
            elif isinstance(facet, HasTextFacet):
                value_label = facetvalue
            elif isinstance(facet, ETypeFacet):
                value_label = self._cw._(facetvalue)
            else:
                try:
                    entity = self._cw.entity_from_eid(facetvalue)
                    attr = getattr(facet, 'target_attr', None)
                    if getattr(facet, 'display_dc_title', None) or not attr:
                        value_label = entity.dc_title()
                    else:
                        value_label = getattr(entity, attr)
                except UnknownEid:
                    value_label = self._cw._(facet.no_relation_label)
                except ValueError:
                    value_label = facetvalue
            all_but_this_facet = list(facet_list)  # copy + list conversion
            all_but_this_facet.remove(facetinfo)
            new_url = self.compute_remove_url(all_but_this_facet, facet_list, form2)
            facet_dico.setdefault(facetid, []).append((value_label, new_url))
        self.render_filters_as_badges(facet_dico, facet_ids, form2,  w)
        w('</div>')

    def render_filters_as_badges(self, facet_dico, facet_ids, form2, w):
        # display new search link
        w('<span>%s %s</span>' % (xml_escape(self._cw._('currently applied filters').capitalize()),
                                   _(':')))
        # display fiter
        for facetid, values in facet_dico.items():
            w(' <span class="facet-badge badge badge-info">%s : %s</span>' % (facet_ids[facetid].capitalize(),
                                                                        ''.join('&#160;<a class="facet-unapply" href="%s">%s&#160;<i class="icon-white icon-remove"></i></a>' % (new_url, value_label) for value_label, new_url in values)))
        start_url = self.start_url(**form2)
        w('&#160;<a href="%(url)s" title="%(title)s" class="remove-all-filters">%(title)s</a>' % {
            'url':start_url, 'title':self._cw._('new search')})

    def start_url(self, **form):
        return self._cw.build_url(self._cw.relative_path(includeparams=False), **form)

    def compute_remove_url(self, all_but_this_facet, facet_list, form):
        if all_but_this_facet:
            return self._cw.build_url(self._cw.relative_path(includeparams=False),
                                             _facet=all_but_this_facet,
                                             **form)
        else:
            return self._cw.build_url(self._cw.relative_path(includeparams=False),
                                             **form)


## magic search / facet query processor #######################################
class FacetQueryProcessor(BaseQueryProcessor):
    """facet+rql query processor.

    Looks for ``_facet`` url parameters, and inserts the corresponding
    RQL restrictions in the base rql query. In other words::

      view?rql=facet+rql:Any X WHERE X has_text "foo"&_facet=etype-facet:the title:Person

    will transforms the original rql query into::

      Any X WHERE X has_text "foo", X is Person
    """
    name = 'facet+rql'
    # It's import to keep the priority low enough to make sure
    # some other query processors is already capable of handling
    # the input query. The only purpose of this query processor
    # is to be called explicitly through urls search as :
    #   view?rql=facet+rql:Any X WHERE ...
    priority = 20
    def preprocess_query(self, uquery):
        self._cw.form['_original_rql_'] = uquery
        facet_list = self._cw.form.get('_facet', ())
        if isinstance(facet_list, str):
            facet_list = (facet_list,)
        uquery = self.build_rql(uquery, facet_list)
        return uquery,


    def build_rql(self, uquery, facet_list):
        # XXX duplication of FilterRQLBuilder code
        form = self._cw.form
        # XXX Union unsupported yet
        select = self._cw.vreg.parse(self._cw, uquery).children[0]
        filtered_variable = select.selection[0].variable
        for facetinfo in facet_list:
            facetid, facetvalue = facetinfo.split(':')
            assert facetid not in self._cw.form, 'namespace clash, I cannot handle this'
            self._cw.form[facetid] = facetvalue
            facet_obj = facetbase.get_facet(self._cw, facetid, select, filtered_variable)
            facet_obj.add_rql_restrictions()
            self._cw.form.pop(facetid)
        return select.as_string()


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (SimpleFacetFilterBox,))
    vreg.register_and_replace(SimpleFacetFilterBox, FilterBox)
