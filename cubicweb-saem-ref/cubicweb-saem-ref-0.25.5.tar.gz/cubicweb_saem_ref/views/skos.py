# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref custom views for skos entities"""


from cubicweb import tags, _
from cubicweb.view import EntityView
from cubicweb.predicates import is_instance
from cubicweb.uilib import js
from cubicweb.view import EntityAdapter
from cubicweb.web import formwidgets as fw
from cubicweb.web.views import baseviews, uicfg

from cubicweb_seda.entities.itree import IContainedToITreeBase
import cubicweb_seda.views.jqtree as jqtree
from cubicweb_skos import views as skos

from . import ImportEntityComponent


afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs

for etype, attr in (('ConceptScheme', 'ark'),
                    ('Concept', 'ark')):
    affk.set_field_kwargs(etype, attr, widget=fw.TextInput({'size': 80}))
    affk.set_field_kwargs(etype, attr, required=False)


_('Import ConceptScheme')  # generate message used by the import component


# Have "in_scheme" inserted in attributes section so that it appears in
# cw_edited and ARK generation hook works. (This overrides uicfg tag in
# cubicweb-skos.)
afs.tag_subject_of(('Concept', 'in_scheme', '*'), 'main', 'attributes')
# Though we don't want to see the field as a Concept can only be created
# through one ConceptScheme, so hide the widget.
affk.set_field_kwargs('Concept', 'in_scheme', widget=fw.HiddenInput())


class SKOSImportComponent(ImportEntityComponent):
    """Component with a link to import a concept scheme from a SKOS file."""
    __select__ = ImportEntityComponent.__select__ & is_instance('ConceptScheme')

    @property
    def import_url(self):
        return self._cw.build_url('add/skossource')


afs.tag_object_of(('*', 'related_concept_scheme', 'ConceptScheme'), 'main', 'hidden')

skos.ConceptSchemePrimaryView.tabs.append(_('saem.lifecycle_tab'))
skos.ConceptPrimaryView.tabs.append(_('saem.lifecycle_tab'))


class ConceptSchemeSameETypeListView(baseviews.SameETypeListView):
    """Override SameETypeListView to display a search action on top"""
    __select__ = baseviews.SameETypeListView.__select__ & is_instance('ConceptScheme')

    def call(self, **kwargs):
        self.search_link()
        super(ConceptSchemeSameETypeListView, self).call(**kwargs)

    def search_link(self):
        """Render a link to search for Concepts within selected ConceptSchemes"""
        rql = 'Any X WHERE X in_scheme S, S eid '
        if len(self.cw_rset) > 1:
            rql += 'IN ({0})'.format(', '.join(str(x[0]) for x in self.cw_rset.rows))
        else:
            rql += str(self.cw_rset[0][0])
        href = self._cw.build_url(rql=rql)
        title = self._cw._('search for concepts of concept schemes')
        self.w(u'<a class="btn btn-default pull-right" href="{href}">{title}</a>'.format(
            href=href, title=title))


class PopoverJQTreeView(jqtree.JQTreeView):

    __select__ = jqtree.JQTreeView.__select__ & is_instance('ConceptScheme')

    def entity_call(self, entity):
        super(PopoverJQTreeView, self).entity_call(entity)
        self._cw.add_onload("$(document).popover({selector:'[data-toggle=\"popover\"]'});")


class ConceptPopoverView(EntityView):
    """Popover view for Concept, to be displayed within a jqtree"""
    __regid__ = 'jqtree.label'
    __select__ = is_instance('Concept')

    def entity_call(self, entity):
        title = entity.dc_title()
        content = u'<dl>'
        for attr in ('definition', 'example'):
            if getattr(entity, attr):
                content += u'<dt>{label}</dt><dd>{value}</dd>'.format(
                    label=self._cw._(attr),
                    value=entity.printable_value(attr, format=u'text/html'))
        content += u'</dl>'
        content += tags.a(self._cw._('view'), href=entity.absolute_url())
        data = {'data-title': title,
                'data-toggle': 'popover',
                'data-content': content,
                'data-html': 'true',
                'data-trigger': 'focus'}
        self.w(tags.a(title, href='javascript:$.noop();', id=str(entity.eid), **data))


class ConceptSchemeConceptsTab(skos.ConceptSchemeConceptsTab):
    """display a SKOS concept scheme tree"""
    __regid__ = 'skos_top_concepts_tab'  # don't use '.' in tab's regid
    __select__ = is_instance('ConceptScheme')

    def render_tree(self, entity, children_rset):
        self._cw.add_js('cubes.saem_ref.js')
        entity.view('jqtree.treeview', w=self.w)


class ConceptSchemeJQTreeAdapter(jqtree.IJQTreeAdapter):
    __select__ = jqtree.IJQTreeAdapter.__select__ & is_instance('ConceptScheme')
    js_can_move_to = js.saem.canMoveTo

    def maybe_parent_of(self):
        return ['Concept']

    def maybe_moved(self):
        return False


class ConceptJQTreeAdapter(jqtree.IJQTreeAdapter):
    __select__ = jqtree.IJQTreeAdapter.__select__ & is_instance('Concept')
    js_can_move_to = js.saem.canMoveTo

    def maybe_parent_of(self):
        return ['Concept']

    def maybe_moved(self):
        return True

    def reparent(self, peid, index):
        parent = self._cw.entity_from_eid(peid)
        self.entity.cw_set(broader_concept=None)
        if parent == self.entity.in_scheme[0]:
            return
        self.entity.cw_set(broader_concept=parent)


class ConceptSchemeITreeBaseAdapter(EntityAdapter):
    __regid__ = 'ITreeBase'
    __select__ = is_instance('ConceptScheme')

    def iterparents(self):
        return iter([])

    def iterchildren(self):
        for concept in self.entity.reverse_in_scheme:
            # Do not treat children of other concepts as children of this concept scheme
            if not concept.broader_concept:
                yield concept

    def is_leaf(self):
        """Returns True if the entity does not have any children."""
        return not self.entity.reverse_in_scheme


class ConceptITreeBaseAdapter(IContainedToITreeBase):
    __regid__ = 'ITreeBase'
    __select__ = is_instance('Concept')

    _children_relations = [('broader_concept', 'object')]


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (
        ConceptSchemeConceptsTab,
    ))
    vreg.register_and_replace(ConceptSchemeConceptsTab,
                              skos.ConceptSchemeConceptsTab)
    from cubicweb_skos.views import ImportConceptSchemeAction
    vreg.unregister(ImportConceptSchemeAction)
    from cubicweb.web.views import cwsources
    vreg.unregister(cwsources.ManageSourcesAction)
