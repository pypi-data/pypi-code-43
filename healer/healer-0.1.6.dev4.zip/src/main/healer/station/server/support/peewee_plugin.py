"""
"""

from __future__ import annotations

import logging
from typing import Any

import peewee
from flask import Flask
from flask import current_app
from flask.templating import render_template
from playhouse.flask_utils import FlaskDB
from playhouse.flask_utils import PaginatedQuery

logger = logging.getLogger(__name__)


class PeeweeDatabaseExt:
    """
    Flask peewee database extension
    """

    def __init__(self, data_name:str='default'):
        super().__init__()
        self.data_name = f"peewee_{data_name}"

    def init_app(self, app:Flask,) -> None:
        assert not self.data_name in app.extensions, f"need solo: {self.data_name}"
        app.extensions[self.data_name] = self.produce_database(app)
        app.before_request(self.perform_open)
        app.teardown_request(self.perform_close)

    def produce_database(self, app:Flask) -> peewee.Database:
        datamake = app.config['DATAMAKE']
        database = datamake()
        assert isinstance(database, peewee.Database), f"wrong maker: {datamake}"
        return database

    def perform_open(self, *args, **kwargs) -> None:
        self.database.connect()

    def perform_close(self, *args, **kwargs) -> None:
        self.database.close()

    @property
    def database(self) -> peewee.Database:
        return current_app.extensions[self.data_name]


class FlaskWrapDB(FlaskDB):

    database:peewee.Database = None

    def __init__(self):
        pass

    def init_app(self, app):
        assert isinstance(self.database, peewee.Database), f"need peewee: {self.database}"
        self._register_handlers(app)


class PagerWrapQuery(PaginatedQuery):
    """
    https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#utilities
    """

    @property
    def has_prev(self) -> bool:
        return self.get_page() > 1

    @property
    def has_next(self) -> bool:
        return self.get_page() < self.get_page_count()

    @property
    def prev_num(self) -> int:
        lower = 1
        page = self.get_page()
        if page > lower:
            return page - 1
        else:
            return lower

    @property
    def next_num(self) -> int:
        upper = self.get_page_count()
        page = self.get_page()
        if page > upper:
            return upper
        else:
            return page + 1

    @property
    def pages(self) -> int:
        return self.get_page_count()

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        page = self.get_page()
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                (num > page - left_current - 1 and
                num < page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def render_object_list(template_name, query, context_variable='object_list',
                paginate_by=20, page_var='page', page=None, check_bounds=True,
                **kwargs):
    paginated_query = PagerWrapQuery(
        query,
        paginate_by=paginate_by,
        page_var=page_var,
        page=page,
        check_bounds=check_bounds,
    )
    kwargs[context_variable] = paginated_query.get_object_list()
    return render_template(
        template_name,
        pagination=paginated_query,
        page=paginated_query.get_page(),
        **kwargs)
