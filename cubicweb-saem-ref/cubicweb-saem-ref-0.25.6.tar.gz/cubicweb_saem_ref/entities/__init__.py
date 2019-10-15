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
"""cubicweb-saem-ref entity's classes"""

from logilab.common.decorators import monkeypatch

from cubicweb import neg_role
from cubicweb.view import Adapter, EntityAdapter
from cubicweb.predicates import match_kwargs, relation_possible, is_instance
from cubicweb.entities import AnyEntity, fetch_config, authobjs, lib

from .. import ark


class ARKIdentifierGeneratorMixin(object):
    __regid__ = 'IARKGenerator'
    __select__ = match_kwargs('naa_what')

    def generate_ark(self):
        """Return a new ARK identifier as unicode"""
        return u'{0}/{1}'.format(self.cw_extra_kwargs['naa_what'], self.assign_name())


class ARKIdentifierGenerator(ARKIdentifierGeneratorMixin, Adapter):
    """Adapter for ARK unique identifier generation"""

    def assign_name(self):
        """Assign and return a new name part of the ARK identifier"""
        naan = int(self.cw_extra_kwargs['naa_what'])
        return ark.generate_ark(self._cw, naan)


class QualifiedARKIdentifierGenerator(ARKIdentifierGeneratorMixin, Adapter):
    """Adapter for ARK identifier generation using a qualifier from an
    existing "base" ARK identifier.
    """
    __abstract__ = True

    @property
    def parent_entity(self):
        raise NotImplementedError

    def assign_name(self):
        match = ark.match(self.parent_entity.ark)
        if not match:
            raise ValueError(
                "ARK identifier for parent entity #%d looks malformattted: %s"
                % (self.parent_entity.eid, self.parent_entity.ark)
            )
        naan = int(self.cw_extra_kwargs['naa_what'])
        # Sanity check to make sure we're not producing ARK identifiers with
        # different NAAN for entities that are supposed to be parent of each
        # others.
        if int(match.group('naan')) != naan:
            raise ValueError(
                "NAAN of parent entity ark:/%s does not match the value of "
                "'naa_what' parameter: %s"
                % (self.parent_entity.ark, naan)
            )
        name = match.group('name')
        qualifier = ark.generate_qualified_ark(self._cw, naan, name)
        return u'/'.join([name, qualifier])


class ConceptARKIdentifierGenerator(QualifiedARKIdentifierGenerator):
    __select__ = (
        QualifiedARKIdentifierGenerator.__select__
        & match_kwargs('in_scheme')
    )

    @property
    def parent_entity(self):
        scheme = self.cw_extra_kwargs['in_scheme']
        if hasattr(scheme, 'eid'):
            return scheme
        return self._cw.entity_from_eid(scheme)


class OUARKIdentifierGenerator(QualifiedARKIdentifierGenerator):
    __select__ = (
        QualifiedARKIdentifierGenerator.__select__
        & match_kwargs('authority')
    )

    @property
    def parent_entity(self):
        authority = self.cw_extra_kwargs['authority']
        if hasattr(authority, 'eid'):
            return authority
        return self._cw.entity_from_eid(authority)


def archive_unit_parent(parent):
    if parent.cw_etype == 'SEDAArchiveTransfer':
        return parent
    elif parent.cw_etype == 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement':
        alt = parent.reverse_seda_seq_alt_archive_unit_archive_unit_ref_id_management[0]
        au = alt.reverse_seda_alt_archive_unit_archive_unit_ref_id[0]
        assert au.cw_etype == 'SEDAArchiveUnit', au
        if au.seda_archive_unit:
            parent = au.seda_archive_unit[0]
            return archive_unit_parent(parent)
        else:
            return au
    else:
        raise ValueError('{} should be target of seda_archive_unit relation'.format(parent))


class SEDAArchiveUnitARKIdentifierGenerator(QualifiedARKIdentifierGenerator):
    __select__ = (
        QualifiedARKIdentifierGenerator.__select__
        & match_kwargs('seda_archive_unit')
    )

    @property
    def parent_entity(self):
        target = self.cw_extra_kwargs['seda_archive_unit']
        if not hasattr(target, 'eid'):
            target = self._cw.entity_from_eid(target)
        return archive_unit_parent(target)


class ArkNAALocator(EntityAdapter):
    """Adapter responsible to retrieve the proper ARK Name Assigning Authority depending on the
    entity type
    """
    __abstract__ = True
    __regid__ = 'IArkNAALocator'

    def naa_what(self):
        """Return the ARK NameAssigningAuthority entity or None if not specified"""
        raise NotImplementedError()


def direct_naa_what(entity):
    # entity is usually not yet created, since ark has to be generated before entity creation
    if 'ark_naa' in getattr(entity, 'cw_edited', {}):
        return entity._cw.entity_from_eid(entity.cw_edited['ark_naa']).what
    elif entity.ark_naa:
        return entity.ark_naa[0].what
    return None


class DirectArkNAALocator(ArkNAALocator):
    """Return NAA specified through the ark_naa relation"""
    __select__ = relation_possible('ark_naa')

    def naa_what(self):
        return direct_naa_what(self.entity)


class AgentArkNAALocator(ArkNAALocator):
    """Return NAA specified through the authority to which the agent belong"""
    __select__ = is_instance('Agent', 'OrganizationUnit')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'authority' in getattr(self.entity, 'cw_edited', {}):
            authority = self._cw.entity_from_eid(self.entity.cw_edited['authority'])
            if authority.ark_naa:
                return authority.ark_naa[0].what
        elif self.entity.authority and self.authority[0].ark_naa:
            return self.authority[0].ark_naa[0].what
        return None


class ConceptArkNAALocator(ArkNAALocator):
    """Return NAA for Concept, through the concept scheme which it belongs to."""
    __select__ = is_instance('Concept')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'in_scheme' in getattr(self.entity, 'cw_edited', {}):
            scheme = self._cw.entity_from_eid(self.entity.cw_edited['in_scheme'])
        elif self.entity.in_scheme:
            scheme = self.entity.in_scheme[0]
        else:
            return None
        return scheme.cw_adapt_to(self.__regid__).naa_what()


class SEDAArchiveUnitArkNAALocator(ArkNAALocator):
    """Return NAA for a SEDAArchiveUnit, either direct or through the
    SEDAArchiveTransfer it belongs to.
    """
    __select__ = is_instance('SEDAArchiveUnit')

    def naa_what(self):
        edited = getattr(self.entity, 'cw_edited', {})
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'seda_archive_unit' in edited or self.entity.seda_archive_unit:
            if 'seda_archive_unit' in edited:
                target = self._cw.entity_from_eid(edited['seda_archive_unit'])
            else:
                target = self.entity.seda_archive_unit[0]
            target = archive_unit_parent(target)
            return target.cw_adapt_to(self.__regid__).naa_what()
        else:
            return direct_naa_what(self.entity)


class ExternalUri(AnyEntity):
    __regid__ = 'ExternalUri'
    fetch_attrs, cw_fetch_order = fetch_config(('uri',))


class EmailAddress(lib.EmailAddress):
    fetch_attrs, cw_fetch_order = fetch_config(['address'])

    def dc_title(self):
        return self.display_address()


@monkeypatch(authobjs.CWUser, methodname='naa')
@property
def naa(self):
    if self.authority and self.authority[0].ark_naa:
        return self.authority[0].ark_naa[0]
    return None


class ISortable(EntityAdapter):
    __regid__ = 'ISortable'
    __abstract__ = True

    role = 'subject'
    rtype = None

    @property
    def parent(self):
        return self.entity.related(self.rtype, self.role, entities=True)[0]

    @property
    def collection(self):
        return self.parent.related(self.rtype, neg_role(self.role), entities=True)


class AuthorityRecordFunctionSortable(ISortable):
    __select__ = is_instance('AgentFunction')

    rtype = 'function_agent'


class AuthorityRecordMandateSortable(ISortable):
    __select__ = is_instance('Mandate')

    rtype = 'mandate_agent'
