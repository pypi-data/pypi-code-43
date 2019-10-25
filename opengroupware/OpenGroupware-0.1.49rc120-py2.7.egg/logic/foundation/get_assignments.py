#
# Copyright (c) 2010, 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
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
# THE SOFTWARE
#
from coils.foundation import CollectionAssignment
from coils.core import Command


class GetAssignedEntities(Command):
    # TODO: Implement collection::get-union command
    __domain__ = "collection"
    __operation__ = "get-assignments"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.collection = params.get('collection', None)
        self.entity_name = params.get('entity_name', None)
        self.as_entity = params.get('as_entity', False)

    def run(self):
        db = self._ctx.db_session()
        query = db.query(CollectionAssignment).filter(
            CollectionAssignment.collection_id == self.collection.object_id,
        )
        query_result = query.all()
        if (len(query_result) > 0):
            if (self.entity_name is None):
                # all assignments regardless of type
                assignments = query_result
            else:
                # get only assignments of specified type
                assignments = []
                assigned_ids = self._ctx.type_manager.group_ids_by_type(
                    [x.assigned_id for x in query_result]
                )
                assigned_ids = assigned_ids.get(self.entity_name, [])
                if (len(assigned_ids) > 0):
                    """
                    WARN: this seems completely redundant??? WTF?
                    Ohh... this is turning the assigned ID back into an
                    assignment ORM entity. HUh.
                    """
                    for assignment in query_result:
                        if assignment.assigned_id in assigned_ids:
                            assignments.append(assignment)
        else:
            assignments = []
        if self.as_entity:
            # return the actual assigned entities, not the assignment entity
            # essentially this deferences the assignment
            entities = self._ctx.type_manager.get_entities(
                [x.assigned_id for x in assignments]
            )
            self.set_return_value(entities)  # return assigned entities
        else:
            self.set_return_value(assignments)  # return assignment entities
