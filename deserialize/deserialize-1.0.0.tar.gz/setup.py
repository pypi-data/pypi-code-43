# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['deserialize']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'deserialize',
    'version': '1.0.0',
    'description': 'A library to make deserialization easy.',
    'long_description': '# deserialize\n\nA library to make deserialization easy. To get started, just run `pip install deserialize`\n\n### How it used to be\n\nWithout the library, if you want to convert:\n\n```\n{\n    "a": 1,\n    "b": 2\n}\n```\n\ninto a dedicated class, you had to do something like this:\n\n```\nclass MyThing:\n\n    def __init__(self, a, b):\n        self.a = a\n        self.b = b\n\n    @staticmethod\n    def from_json(json_data):\n        a_value = json_data.get("a")\n        b_value = json_data.get("b")\n\n        if a_value is None:\n            raise Exception("\'a\' was None")\n        elif b_value is None:\n            raise Exception("\'b\' was None")\n        elif type(a_value) != int:\n            raise Exception("\'a\' was not an int")\n        elif type(b_value) != int:\n            raise Exception("\'b\' was not an int")\n\n        return MyThing(a_value, b_value)\n\nmy_instance = MyThing.from_json(json_data)\n```\n\n### How it is now\n\nWith `deserialize` all you need to do is this:\n\n```\nimport deserialize\n\nclass MyThing:\n    a: int\n    b: int\n\nmy_instance = deserialize.deserialize(MyThing, json_data)\n```\n\nThat\'s it. It will pull out all the data and set it for you type checking and even checking for null values.\n\nIf you want null values to be allowed though, that\'s easy too:\n\n```\nfrom typing import Optional\n\nclass MyThing:\n    a: Optional[int]\n    b: Optional[int]\n```\n\nNow `None` is a valid value for these.\n\nTypes can be nested as deep as you like. For example, this is perfectly valid:\n\n```\nclass Actor:\n    name: str\n    age: int\n\nclass Episode:\n    title: str\n    identifier: st\n    actors: List[Actor]\n\nclass Season:\n    episodes: List[Episode]\n    completed: bool\n\nclass TVShow:\n    seasons: List[Season]\n    creator: str\n```\n\n## Advanced Usage\n\n### Custom Keys\n\nIt may be that you want to name your properties in your object something different to what is in the data. This can be for readability reasons, or because you have to (such as if your data item is named `__class__`). This can be handled too. Simply use the `key` annotation as follows:\n\n```\n@deserialize.key("identifier", "id")\nclass MyClass:\n    value: int\n    identifier: str\n```\n\nThis will now assign the data with the key `id` to the field `identifier`. You can have multiple annotations to override multiple keys.\n\n### Ignored Keys\n\nYou may want some properties in your object that aren\'t loaded from disk, but instead created some other way. To do this, use the `ignore` decorator. Here\'s an example:\n\n```\n@deserialize.ignore("identifier")\nclass MyClass:\n    value: int\n    identifier: str\n```\n\nWhen deserializing, the library will now ignore the `identifier` property.\n\n### Parsers\n\nSometimes you\'ll want something in your object in a format that the data isn\'t in. For example, if you get the data:\n\n```\n{\n    "successful": True,\n    "timestamp": 1543770752\n}\n```\n\nYou may want that to be represented as:\n\n```\nclass Result:\n    successful: bool\n    timestamp: datetime.datetime\n```\n\nBy default, it will fail on this deserialization as the value in the data is not a timestamp. To correct this, use the `parser` decorator to tell it a function to use to parse the data. E.g.\n\n```\n@deserialize.parser("timestamp", datetime.datetime.fromtimestamp)\nclass Result:\n    successful: bool\n    timestamp: datetime.datetime\n```\n\nThis will now detect when handling the data for the _key_ `timestamp` and run it through the parser function supplied before assigning it to your new class instance.\n\nThe parser is run _before_ type checking is done. This means that if you had something like `Optional[datetime.datetime]`, you should ensure your parser can handle the value being `None`. Your parser will obviously need to return the type that you have declared on the property in order to work.',
    'author': 'Dale Myers',
    'author_email': 'dale@myers.io',
    'url': 'https://github.com/dalemyers/deserialize',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
