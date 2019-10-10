import unittest

from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.repositories.custom_property_repository import CustomPropertyRepository
from rox.core.repositories.roxx.properties_extensions import PropertiesExtensions
from rox.core.roxx.parser import Parser


class PropertiesExtensionsTests(unittest.TestCase):
    def test_roxx_properties_extensions_string(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.STRING, 'test'))

        self.assertEqual(True, parser.evaluate_expression('eq("test", property("testKey"))').value)

    def test_roxx_properties_extensions_int(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.INT, 3))

        self.assertEqual(True, parser.evaluate_expression('eq(3, property("testKey"))').value)

    def test_roxx_properties_extensions_float(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.FLOAT, 3.3))

        self.assertEqual(True, parser.evaluate_expression('eq(3.3, property("testKey"))').value)

    def test_roxx_properties_extensions_with_context_string(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.STRING,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 'test'}

        self.assertEqual(True, parser.evaluate_expression('eq("test", property("CustomPropertyTestKey"))', context).value)

    def test_roxx_properties_extensions_with_context_int(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.INT,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 3}

        self.assertEqual(True, parser.evaluate_expression('eq(3, property("CustomPropertyTestKey"))', context).value)

    def test_roxx_properties_extensions_with_context_int_with_string(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.INT,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 3}

        self.assertEqual(False, parser.evaluate_expression('eq("3", property("CustomPropertyTestKey"))', context).value)

    def test_roxx_properties_extensions_with_context_int_not_equal(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('CustomPropertyTestKey', CustomPropertyType.INT,
                                                                      lambda c: c.get('ContextTestKey')))
        context = {'ContextTestKey': 3}

        self.assertEqual(False, parser.evaluate_expression('eq(4, property("CustomPropertyTestKey"))', context).value)

    def test_unknown_property(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.STRING, 'test'))

        self.assertEqual(False, parser.evaluate_expression('eq("test", property("testKey1"))').value)

    def test_null_property(self):
        custom_property_repository = CustomPropertyRepository()
        parser = Parser()

        roxx_properties_extensions = PropertiesExtensions(parser, custom_property_repository)
        roxx_properties_extensions.extend()

        custom_property_repository.add_custom_property(CustomProperty('testKey', CustomPropertyType.STRING,
                                                                      lambda c: None))

        self.assertEqual(True, parser.evaluate_expression('eq(undefined, property("testKey"))').value)
