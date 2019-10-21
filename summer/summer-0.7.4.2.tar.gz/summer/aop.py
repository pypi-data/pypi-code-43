# Copyright (C) 2009-2019 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Provides summer *AOP* functionality.

You can find here most useful decorators :py:func:`transactional` for SQL
transaction support and :py:func:`ldapaop`.

"""

import functools
import logging
import types

from .sf import SessionFactory
from .lsf import LdapSessionFactory

logger = logging.getLogger(__name__)


def transactional(method: types.FunctionType) -> types.FunctionType:
    """Method decorator marking method to be transactional.

    Every decorated method behaves as follows:

    * if no transaction is active and database is *not* in autocommit mode,
      start a new transaction, doing commit/rollback at the end

    * if there is a transaction, just simple continue within the
      transaction without doing commit/rollback at the end (that is left to
      the top-most transactional method)

    Args:

        method (types.FunctionType): function to be decorated

    Returns:

        (types.FunctionType): decorated function

    """
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = method.__name__
    logger.debug("method %s decorated as transactional", mame)
    transactional.session_factory = None

    @functools.wraps(method)
    def _transactional(*args, **kwargs) -> object:
        assert isinstance(transactional.session_factory, SessionFactory)
        session = transactional.session_factory.session
        logger.debug("tx begin with session %s", session)
        active = session.active
        try:
            if active:
                logger.debug("tx active, continue")
            else:
                session.begin()
                logger.debug("tx not active, started")
            result = method(*args, **kwargs)
            if active:
                logger.debug("tx active, no commit")
            else:
                session.commit()
                logger.debug("tx commit")
        except Exception as ex:
            session.rollback()
            logger.exception("tx rollback")
            raise ex
        finally:
            if active:
                logger.debug("tx active, not closing")
            else:
                # session can outlive the transaction to be reused later on
                # session.close()
                # logger.debug("tx closed")
                pass
        return result

    return _transactional


def ldapaop(method: types.FunctionType) -> types.FunctionType:
    """Method decorator marking method to be run in LDAP session.  Analogy to
    :py:func:`summer.aop.transactional` with same logic.

    Intended use case for this decorator is to decorate
    :py:class:`summer.ldapdao.LdapEntityDao` methods and then access
    current *ldap3* session/connection by using
    :py:attr:`summer.ldapdao.LdapDao.session` from within the *DAO* method.
    Thus you can access *ldap3* session/connection (and manipulate data),
    and still have the transaction boundaries defined on top of your
    business methods.

    Args:

        method (types.FunctionType): function to be decorated

    Returns:

        (types.FunctionType): decorated function

    """
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = method.__name__
    logger.debug("method %s decorated as ldapaop", mame)
    ldapaop.ldap_session_factory = None

    @functools.wraps(method)
    def _ldapaop(*args, **kwargs) -> object:
        assert isinstance(ldapaop.ldap_session_factory, LdapSessionFactory)
        session = ldapaop.ldap_session_factory.session
        logger.debug("lx begin with session %s", session)
        active = session.active
        try:
            if active:
                logger.debug("lx active, continue")
            else:
                session.bind()
                logger.debug("lx not active, bounded")
            result = method(*args, **kwargs)
            logger.debug("lx ok")
        except Exception as ex:
            logger.exception("lx error")
            raise ex
        finally:
            if active:
                logger.debug("lx active, not closing")
            else:
                # session can outlive single call to be reused later on
                # session.unbound()
                # logger.debug("lx session unbounded")
                pass
        return result

    return _ldapaop
