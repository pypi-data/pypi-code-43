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
"""cubicweb-saem-ref views related to SEDA"""

from cubicweb.predicates import (
    has_related_entities,
    is_instance,
    objectify_predicate,
)
from cubicweb.web import formwidgets as fw
from cubicweb.web.views import uicfg

from cubicweb_seda.views import (
    CONTENT_ETYPE,
    archivetransfer,
    archiveunit,
    rtags_from_rtype_role_targets,
    simplified
)


affk = uicfg.autoform_field_kwargs
afs = uicfg.autoform_section
pvs = uicfg.primaryview_section

# also hide transferring and archival agency
for rtype in ('seda_transferring_agency', 'seda_archival_agency'):
    afs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'main', 'hidden')
    pvs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'hidden')

pvs.tag_object_of(('*', 'use_profile', '*'), 'hidden')
afs.tag_object_of(('*', 'use_profile', '*'), 'main', 'hidden')

pvs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'hidden')
afs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'main', 'hidden')

# Have "seda_archive_unit" inserted in attributes section so that it appears
# in cw_edited and ARK generation hook works.
afs.tag_subject_of(('SEDAArchiveUnit', 'seda_archive_unit', '*'), 'main', 'attributes')
# Though we don't want to see the field in form, so hide the widget.
affk.set_field_kwargs('SEDAArchiveUnit', 'seda_archive_unit', widget=fw.HiddenInput())


archivetransfer.ArchiveTransferTabbedPrimaryView.tabs.append('saem.lifecycle_tab')


@objectify_predicate
def creating_seda_archive_unit(cls, req, **kwargs):
    for linkto in req.list_form_param('__linkto'):
        rtype, _, role = linkto.split(':')
        if (rtype, role) == ('seda_archive_unit', 'subject'):
            return 1
    return 0


nested_archiveunit_afs = afs.derive(
    __name__,
    is_instance('SEDAArchiveUnit')
    & (has_related_entities('seda_archive_unit')
       | creating_seda_archive_unit())
)
nested_archiveunit_afs.tag_subject_of(('SEDAArchiveUnit', 'ark_naa', '*'),
                                      'main', 'hidden')

nested_archiveunit_pvs = pvs.derive(
    __name__,
    is_instance('SEDAArchiveUnit')
    & has_related_entities('seda_archive_unit')
)
nested_archiveunit_pvs.tag_subject_of(('SEDAArchiveUnit', 'ark_naa', '*'),
                                      'hidden')


# Hide "identifiant pour le service versant" which should be automatically
# filled.
class SimplifiedContentMainView(archiveunit.SimplifiedContentMainView):

    rtype_role_targets = archiveunit.SimplifiedContentMainView.rtype_role_targets[:]
    rtype_role_targets.remove(
        ('seda_transferring_agency_archive_unit_identifier', 'object', None)
    )
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


simplified.simplified_afs.tag_object_of(
    ('*', 'seda_transferring_agency_archive_unit_identifier', CONTENT_ETYPE),
    'main', 'hidden',
)


class ContentMainView(archiveunit.ContentMainView):

    rtype_role_targets = archiveunit.ContentMainView.rtype_role_targets[:]
    rtype_role_targets.remove(
        ('seda_transferring_agency_archive_unit_identifier', 'object', None)
    )
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [
        ContentMainView,
        SimplifiedContentMainView,
    ])
    vreg.register_and_replace(ContentMainView, archiveunit.ContentMainView)
    vreg.register_and_replace(SimplifiedContentMainView, archiveunit.SimplifiedContentMainView)
