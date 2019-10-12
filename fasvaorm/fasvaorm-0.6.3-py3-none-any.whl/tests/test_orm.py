import unittest

import fasvaorm
from fasvaorm import get_session, EngineNotInitializedError, init_engine, init_session_factory, init_session, \
    set_engine, cleanup, get_engine, get_session_factory
from tests.base import DB_URL


class TestEngine(unittest.TestCase):
    def setUp(self):
        super().setUp()

        cleanup()

    def test_create(self):

        engine = init_engine(url=DB_URL)
        self.assertIsNotNone(engine)

        self.assertEqual(get_engine(), engine)


class TestCreateSessionWithoutEngine(unittest.TestCase):

    def setUp(self):
        super().setUp()

        cleanup()

    def test_get_session_without_engine_initialization(self):
        """
        Test if the EngineNotInitializedError is raised if we try to get a session without initialization.
        """
        with self.assertRaises(EngineNotInitializedError):
            get_session()


class TestCreateSessionWithEngine(unittest.TestCase):

    def test_get_session_with_engine_without_factory(self):

        engine = init_engine(url=DB_URL)
        self.assertIsNotNone(engine)

        session = get_session()
        self.assertIsNotNone(session)

        fasvaorm.close_session(session)

    def test_get_session_with_engine_and_factory(self):
        cleanup()

        engine = init_engine(url=DB_URL)
        self.assertIsNotNone(engine)

        factory = init_session_factory(engine=engine)
        self.assertIsNotNone(factory)

        session = factory()
        self.assertIsNotNone(session)

        session2 = factory()
        self.assertNotEqual(session, session2)


class TestCreateFactoryWithoutEngine(unittest.TestCase):

    def test_init_factory_without_engine(self):

        cleanup()

        # test init factory by call of function
        with self.assertRaises(EngineNotInitializedError):
            init_session_factory()

        # test init factory by getting it
        with self.assertRaises(EngineNotInitializedError):
            get_session_factory()

    def test_init_factory_with_engine(self):
        cleanup()

        engine = init_engine(url=DB_URL)
        factory = init_session_factory(engine)

        self.assertIsNotNone(factory)
        self.assertEqual(get_session_factory(), factory)
