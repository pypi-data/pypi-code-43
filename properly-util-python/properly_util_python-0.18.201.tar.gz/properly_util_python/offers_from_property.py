import warnings

from boto3.dynamodb.conditions import Key
from properly_util_python.dynamo_utils import get_dynamo_item, get_dynamo_items
from properly_util_python.dynamo_helper import DynamoHelperBase
from properly_util_python.table_helper import TableHelper


class OffersFromProperty:

    def __init__(self, dynamo_helper: DynamoHelperBase):
        self.dynamo_helper = dynamo_helper
        self.table_helper = TableHelper(dynamo_helper)

        # Initialize lazy loading offers
        self.property_id = None
        self.property_item = None

    def get_offers_with_property_id(self, property_id):
        """
        Returns all relevant offers for the property ID
        :param property_id: The Property ID
        :return: List of Offers
        """
        property_item = self.get_property(property_id)
        offer_items = self._get_dynamo_offer_items_with_property_id(TableHelper.OFFER_TABLE_NAME,property_id)

        return offer_items

    def _get_dynamo_offer_items_with_property_id(self,offer_table,property_id):

        table_name_with_environment = self.table_helper.get_table_name(offer_table)
        table_filter = {
            'IndexName': 'propertyId-index',
            'KeyConditionExpression': Key('propertyId').eq(property_id)
        }

        return get_dynamo_items(table_name_with_environment, table_filter, table_get_type='query')

    def _get_dynamo_property_item_with_property_id(self,property_table,property_id):

        table_name_with_environment = self.table_helper.get_table_name(property_table)

        return get_dynamo_item(table_name_with_environment, property_id)

    def get_property(self, property_id):
        """
        Gets the Property by ID.
        This will get lazy loaded once per ID.
        If subsequent other calls uses the same property ID, it will use the lazy loaded instance.
        This saves multiple calls to the database and allows easy access to the offer from multiple places.
        :param property_id: The ID of the property.
        :return: The property dictionary
        """
        if not self.property_item or self.property_id != property_id:
            self.property_id = property_id
            self.property_item = self._get_dynamo_property_item_with_property_id(TableHelper.PROPERTY_TABLE_NAME,property_id)

        return self.property_item

