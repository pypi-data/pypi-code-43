# Copyright (c) 2010, 2018
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
from coils.foundation import KVC
from coils.core import CoilsException


class EnterpriseCommand(object):

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command(
            'enterprise::get', id=object_id, access_check=access_check,
        )

    def set_contacts(self):
        '''
        [ {'entityName': 'assignment',
           'objectId': 10634162,
           'sourceEntityName': 'Enterprise',
           'sourceObjectId': 10290,
           'targetEntityName': 'Contact',
           'targetObjectId': 10100}]
        The targetObjectId is the contact id, how assignments are represented
        depends on thier context; in a Contact entity the targetObjectId is
        the enterprise id. The source is the entity being rendered.
        '''
        assignments = KVC.subvalues_for_key(
            self.values, ['_CONTACTS', 'contacts'], default=None,
        )
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('childId', None))
                if (_id is not None):
                    _ids.append(_id)
            self._ctx.run_command(
                'enterprise::set-contacts',
                enterprise=self.obj, contact_ids=_ids,
            )

    def process_business_cards(self):
        contacts = KVC.subvalues_for_key(
            self.values, ['_CONTACTS', 'contacts'], default=None,
        )
        if not isinstance(contacts, list):
            """
            short-circuit if the contacts value is not a list, we need
            something we know we can safely enumerate
            """
            return
        for contact_dict in contacts:
            contact = self._ctx.run_command(
                'contact::new', values=contact_dict,
            )
            if not contact:
                raise CoilsException(
                    'Unable to create contact from business card data'
                )
            self._ctx.flush()
            self._ctx.run_command(
                'object::copy-access', source=self.obj, target=contact,
            )
            self._ctx.run_command(
                'company::assign', source=self.obj, target=contact,
            )
            self.log.info(
                'Created OGo#{0} [Contact] via businessCard on '
                'OGo#{1} [Enterprise]'.format(
                    contact.object_id, self.obj.object_id,
                )
            )
