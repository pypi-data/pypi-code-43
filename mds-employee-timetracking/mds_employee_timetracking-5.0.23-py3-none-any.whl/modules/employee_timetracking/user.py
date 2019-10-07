# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL
from trytond.pool import Pool, PoolMeta

__all__ = ['User']
__metaclass__ = PoolMeta


class User(ModelSQL, ModelView):
    "User"
    __name__ = "res.user"
    
    @classmethod
    def _get_preferences(cls, user, context_only=False):
        """ send converter-dict to client,
            to reduce formatting of timedelta to hhh:mm
        """
        res1 = super(User, cls)._get_preferences(user, context_only)
        res1['tdconv_hhhmm'] = {'s': 1, 'm': 60, 'h': 3600, 'w':1, 'M':1, 'Y':1}
        return res1

# end User
