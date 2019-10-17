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

"""Main entry point to the program."""

# usual imports
import logging
import summer

# import ApplicationContext
from .appcontext import ctx

# import for demo purposes
from .model import Category, DeclarativeFooEntity

# configure logging as soon as possible
logger = logging.getLogger(__name__)


def main(args):
    """Entry point to our program."""
    logger.info("sample started")
    # create the sample database
    ctx.session_factory.create_schema()
    # run demonstration
    do_demonstration()
    logger.info("sample finished")


def do_demonstration():
    mark = "PROGRAM OUTPUT>"

    # l10n
    logger.info("%s test localization -- %s", mark, _("localized message"))

    # db
    logger.info("let's create some objects and persist them")
    category_dao = ctx.category_dao
    for i in range(1, 16):
        cat = Category()
        cat.order = i
        cat.code = "code_%02d" % (cat.order,)
        category_dao.save(cat)

    # we go through result set using paging
    logger.info(
        "let's iterate using db paging through what we have just persisted")
    cat_filter = summer.Filter(1, 5)
    for page in range(1, 4):
        cat_filter.page = page
        logger.info("%s page %d", mark, cat_filter.page)
        for cat in category_dao.find(cat_filter):
            logger.info("%s %s", mark, cat)

    # db declarative entity
    numbers = range(1, 5)
    s = ctx.session_factory.sqlalchemy_session
    for i in numbers:
        s.add(DeclarativeFooEntity(name="name_%d" % (i,)))
    s.commit()
    col = s.query(DeclarativeFooEntity).all()
    s.commit()
    assert len(numbers) == len(col)

    # ldap
    logger.info("let's use LDAP demo query for arbitrary objects (not all of them, just those with ou=users)")
    user_manager = ctx.user_manager
    for user in user_manager.find():
        logger.info("%s %s", mark, user)
