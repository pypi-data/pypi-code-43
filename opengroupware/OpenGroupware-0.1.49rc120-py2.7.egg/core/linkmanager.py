#!/usr/bin/python
# Copyright (c) 2010, 2013, 2015, 2018
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import NoResultFound
from coils.foundation import ObjectLink


class LinkManager(object):
    __slots__ = ('_ctx')

    def __init__(self, ctx):
        self._ctx = ctx

    @property
    def log(self):
        return self._ctx.log

    def links_to(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).\
            filter(ObjectLink.target_id == entity.object_id)
        data = query.all()
        query = None
        return data

    def links_from(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).\
            filter(ObjectLink.source_id == entity.object_id)
        data = query.all()
        query = None
        return data

    def links_to_and_from(self, entity, kind=None):
        db = self._ctx.db_session()
        if kind:
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        or_(
                            ObjectLink.source_id == entity.object_id,
                            ObjectLink.target_id == entity.object_id,
                        ),
                        ObjectLink.kind == kind,
                    )
                )
        else:
            query = db.query(ObjectLink).\
                filter(
                    or_(
                        ObjectLink.source_id == entity.object_id,
                        ObjectLink.target_id == entity.object_id,
                    )
                )

        query = query.order_by(
            ObjectLink.source_id,
            ObjectLink.target_id,
            ObjectLink.kind,
        )
        data = query.all()
        query = None
        return data

    def links_between(self, entity1, entity2, kind=None):
        db = self._ctx.db_session()
        if kind is None:
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        ObjectLink.source_id.in_((entity1.object_id,
                                                  entity2.object_id, )),
                        ObjectLink.target_id.in_((entity1.object_id,
                                                  entity2.object_id, )),
                    )
                )
        else:
            # A link kind was specified
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        ObjectLink.source_id.in_((entity1.object_id,
                                                  entity2.object_id, )),
                        ObjectLink.target_id.in_((entity1.object_id,
                                                  entity2.object_id, )),
                        ObjectLink.kind == kind,
                    )
                )

        query = query.order_by(ObjectLink.source_id,
                               ObjectLink.target_id,
                               ObjectLink.kind, )
        data = query.all()
        query = None
        return data

    def link(self, source, target, kind='generic', label=None):
        # TODO: Give a new link a label if none was provided
        db = self._ctx.db_session()
        if (kind is None):
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        ObjectLink.source_id == source.object_id,
                        ObjectLink.target_id == target.object_id,
                    )
                )
        else:
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        ObjectLink.source_id == source.object_id,
                        ObjectLink.target_id == target.object_id,
                        ObjectLink.kind == kind,
                    )
                )
        links = query.all()
        # TODO: Tidy
        if links:
            link = links[0]
            if not(link.label == label):
                link.label = label
            return link
        else:
            link = ObjectLink(source, target, kind, label)
            self._ctx.db_session().add(link)
            self.log.debug(
                'Linking OGo#{0} -> OGo#{1}; kind: "{2}".'
                .format(
                    source.object_id,
                    target.object_id,
                    link.kind,
                )
            )
            return link

    def unlink(self, source, target, kind='generic'):
        """
        Remove the described link between the source and the target. Returns
        True if a link is found and deleted, False otherwise.
        """
        # TODO: verify at least one side has modification rights
        db = self._ctx.db_session()
        if kind is None:
            query = db.query(ObjectLink).filter(
                and_(
                    ObjectLink.source_id == source.object_id,
                    ObjectLink.target_id == target.object_id,
                )
            )
        else:
            query = db.query(ObjectLink).filter(
                and_(
                    ObjectLink.source_id == source.object_id,
                    ObjectLink.target_id == target.object_id,
                    ObjectLink.kind == kind,
                )
            )

        try:
            link = query.one()
        except NoResultFound:
            return False
        else:
            self._ctx.db_session().delete(link)
        return True

    # Private method, do not use externally
    def _is_linked(self, source_id, target_id, kind):
        db = self._ctx.db_session()
        if kind:
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        ObjectLink.source_id == source_id,
                        ObjectLink.target_id == target_id,
                    )
                )
        else:
            query = db.query(ObjectLink).\
                filter(
                    and_(
                        ObjectLink.source_id == source_id,
                        ObjectLink.target_id == target_id,
                        ObjectLink.kind == kind,
                    )
                )
        result = query.all()
        if query.all():
            return result[0]
        else:
            return False

    # Private method, do not use externally
    def _get_entity(self, object_id):
        return self._ctx.type_manager.get_entity(
            object_id, repair_enabled=False,
        )

    def sync_links(self, entity, links_in):

        db = self._ctx.db_session()

        # Assume we are going to delete all the existing links
        removes = [link.object_id for link in self.links_to_and_from(entity)]

        for link in links_in:

            if isinstance(link, dict):
                source_id = link.get('source_id')
                target_id = link.get('target_id')
                kind = link.get('kind', 'generic')
                label = link.get('label', None)
            else:
                # assuming an ObjectLink entity
                source_id = link.source_id
                target_id = link.target_id
                kind = link.kind
                label = link.label

            """
            Do not go to the type manager to discover the entity if the entity
            is the context of the sync-links operation; get_entity will not
            be able to find an entity that has not yet been committed to the
            ORM - as in the case of a newly created entity.
            """
            if source_id == entity.object_id:
                # entity is the source
                source = entity
            else:
                source = self._ctx.type_manager.get_entity(source_id)
            if target_id == entity.object_id:
                # entity is the target
                target = entity
            else:
                target = self._ctx.type_manager.get_entity(target_id)
            if (source is None) or (target is None):
                """
                One end of the link cannot be materialized, possible
                permissions issue; this link will be ignored for syncing.
                We do not want to delete it as it could be valid but a
                permissions issue; if an entity is deleted the watcher
                should handle any required clean-up of derelict references.
                """
                link_ = self._is_linked(source_id, target_id, kind)
                if link_:
                    if link_.object_id in removes:
                        self.log.debug(
                            'ObjectLink sync ignoring link between source '
                            'OGo#{0} and target OGo#{1} as one side cannot '
                            'be materialized'
                            .format(source_id, target_id, )
                        )
                        removes.remove(link_.object_id)
                continue

            # this will update the label if required or create the link
            link = self.link(source, target, kind=kind, label=label)
            if link.object_id in removes:
                self.log.debug(
                    'Link OGo#{0} OGo#{1} -> OGo#{2} persisted; kind: "{3}".'
                    .format(
                        link.object_id,
                        source.object_id,
                        target.object_id,
                        link.kind,
                    )
                )
                removes.remove(link.object_id)
        # delete existing links that the client did not specify
        if removes:
            db.query(ObjectLink).\
                filter(ObjectLink.object_id.in_(removes)).\
                delete(synchronize_session='fetch')

    def copy_links(self, source, target):
        counter = 0
        for link in self.links_to_and_from(source):
            new_source = new_target = None
            if link.source_id == source.object_id:
                new_source = target
                new_target = self._ctx.type_manager.get_entity(link.target_id)
            else:
                new_source = self._ctx.type_manager.get_entity(link.source_id)
                new_target = target
            if new_source and new_target:
                self.link(new_source,
                          new_target,
                          kind=link.kind,
                          label=link.label, )
                counter += 1
        return counter
