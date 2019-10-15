
from properly_util_python.dynamo_helper import DynamoHelperBase
from properly_util_python.table_helper import TableHelper
from properly_util_python.dynamo_data_utils import DynamoData


class OfferUtils:

    def __init__(self, dynamo_helper: DynamoHelperBase):

        self.dynamo_helper = dynamo_helper
        self.table_helper = TableHelper(self.dynamo_helper)

    def get_property_and_user_from_offer(self, offer_dict):
        property_table = self.table_helper.get_table(TableHelper.PROPERTY_TABLE_NAME)
        user_table = self.table_helper.get_table(TableHelper.USER_TABLE_NAME)

        property_id = offer_dict.get('propertyId')
        user_id = offer_dict.get('ownerId')
        if property_id is None or user_id is None:
            return None, None

        response = property_table.get_item(Key={'id': property_id})
        item = response.get('Item')
        property_dict = DynamoData.to_dict(item)

        response = user_table.get_item(Key={'id': user_id})
        item = response.get('Item')
        user_dict = DynamoData.to_dict(item)

        return property_dict, user_dict

    def build_offer_with_property_and_user(self, offer_dict: dict, property_dict: dict, user_dict: dict):

        # Consider adding filtering similar to:
        # https://github.com/GoProperly/hig-offer-api/blob/78e21aa0b962ee859a4e9e6a941f79612899f56b/offer/src/offer_handler.py#L237

        if offer_dict is None or property_dict is None or user_dict is None:
            msg = 'Non null required offer: {} property: {} user: {} '.format(offer_dict, property_dict, user_dict)
            raise RuntimeError(msg)

        offer_dict['property'] = property_dict
        offer_dict['user'] = user_dict

        return offer_dict


