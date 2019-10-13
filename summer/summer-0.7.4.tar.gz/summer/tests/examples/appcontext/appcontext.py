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

"""This module demonstrates the very core usage of the *summer* application
framework.

For people familiar with Java spring framework -- this file defines the
:py:class:`ApplicationContext` class.  All configuration is placed directly
in your *Python* code.

Among other resources somewhere in your application you will have a file
like this -- a file defining a 'context' for your application business
layer.  You can of course have more layers, more contexts, ...

Such a context class serves as a container for your business objects.  Once
you have you context initialized, you may usually access all your
application's services from one single place.  The best thing is, that all the
creation, dependency and initialization logic among your business objects
is defined there.

Objects deployed into the context should be stateless and can be treated as
singletons (but there is no rule for that and you can deploy whatever you
want in any way you like it) -- please see any discussion on inversion of
control containers (IoC) for more info.

This simple example shows:

  1. sample context definition with very simple declarative transaction
  handling

  2. basic concept how to use logging and custom configuration -- logging
  config (defined by Python stdlib) and most simple summer framework config

  3. So you get an idea, what its all about :-)

"""

# usual imports
import logging.config
import os.path
import typing

# import the summer framework
import summer

# import configuration
from . import conf

# reasonable and simple convention on getting a logger
LOGGING_CFG = os.path.join(os.path.dirname(__file__), "logging.cfg")
logging.config.fileConfig(LOGGING_CFG)
logger = logging.getLogger(__name__)


class CustomDao(summer.Dao):
    """Dao object for custom persistence logic.

    Persistence logic is usually managed by a Dao objects; usually
    you will subclass those provided by *summer*, see
    :py:class:`summer.dao.Dao` for details.

    """

    def __init__(self, session_factory):
        summer.Dao.__init__(self, session_factory)

    def find(self, filter: summer.Filter) -> typing.List[summer.Entity]:
        """Dao methods usually executed within transaction context.
        They access session through provided attributes (if derived from
        :py:class:`summer.Dao` or directly using :py:class:`summer.SessionFactory`.
        """
        session = self.session_factory.session
        assert session is not None

        sqlalchemy_session1 = self.session_factory.sqlalchemy_session
        sqlalchemy_session2 = self.session
        assert sqlalchemy_session1 is sqlalchemy_session2

        connection1 = self.session_factory.connection.connection
        connection2 = self.connection.connection
        assert connection1 is connection2
        return []


class EntityManager(object):
    """This class manages entities using the Dao, probably it adds some
    business logic for creating a new objects and such.

    """

    def __init__(self, entity_dao):
        self.entity_dao = entity_dao

    @summer.transactional
    def find(self):
        """Method is marked as transactional.  Decorator implements a transactional advice.
        """
        logger.info("executing dao find method within transaction")
        self.entity_dao.find(summer.Filter.get_default())


class ApplicationContext(summer.Context):
    """The much anticipated application context class."""

    def __init__(self):
        """:py:class:`summer.context.Context` has some more arguments, but usually
        you just provide reference to :py:class:`summer.sf.SessionProvider`
        instance, in most cases the supplied
        :py:class:`summer.sf.DefaultSessionProvider` is sufficient to be
        used directly.

        """
        summer.Context.__init__(self, summer.DefaultSessionProvider(conf.sqlalchemy_uri))

    def orm_init(self):
        """Do additional ORM setup for your application.  For now, just ignore it.

        You may use :py:class:`summer.TableDefinitios` and
        :py:class:`summer.ClassMappings` to ease ORM initialization.

        """
        pass

    def context_init(self):
        """Please see :py:method:`summer.context.Context.context_init`.

        This method gets called once the basic context initialization is
        done.  You may deploy your business objects there.

        """

        # let's deploy our only DAO -- any data access object should have a
        # reference to session factory to be able to obtain session any time
        # it accesses data
        self.entity_dao = CustomDao(self.session_factory)

        # let's deploy our only manager -- main business object
        self.entity_manager = EntityManager(self.entity_dao)


# create application context -- you can create one or several instances of
# your application context, but it is usual to create single instance
# (singleton) and define it as module level reference
ctx = ApplicationContext()
