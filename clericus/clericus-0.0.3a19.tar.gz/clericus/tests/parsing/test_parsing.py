import unittest
import asyncio

from ...parsing import DictParser, handleAcceptHeader
from ...parsing.fields import StringField, DictField
from ..test_case import async_test


class TestParsing(unittest.TestCase):
    @async_test
    async def test_moo(self):
        # self.assertEqual(1, 1)
        class dp(DictParser):
            stringOne = StringField()
            stringTwo = StringField()
            dictOne = DictField(
                fields={
                    "stringThree": StringField(),
                    "stringFour": StringField(),
                    "dictTwo": DictField({}),
                }
            )

        parsed = await dp().parse({
            "stringOne": "moo",
            "stringTwo": "cow",
            "dictOne": {
                "stringThree": "moo",
                "stringFour": "cow",
                "dictTwo": {
                    "x": 1
                }
            }
        })

        self.assertEqual(parsed["stringOne"], "moo")
        self.assertEqual(parsed["stringTwo"], "cow")
        self.assertEqual(parsed["dictOne"]["stringThree"], "moo")
        self.assertEqual(parsed["dictOne"]["stringFour"], "cow")
        self.assertEqual(parsed["dictOne"]["dictTwo"]["x"], 1)


class TestAcceptHeaderParsing(unittest.TestCase):
    def test_simple_parsing(self):
        contentType, parameters = handleAcceptHeader(
            "text/*;q=0.3, text/html;q=0.7, text/html;level=1, text/html;level=2;q=0.4, */*;q=0.5",
            ["text/html", "text/plain"],
        )
        self.assertEqual(contentType, "text/html")
        self.assertEqual(parameters["level"], "1")


if __name__ == '__main__':
    unittest.main()