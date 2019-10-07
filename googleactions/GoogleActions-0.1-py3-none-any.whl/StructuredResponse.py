from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .OrderUpdate import OrderUpdate
from .Price import Price
from .Action import Action
from .OrderState import OrderState
from .UserNotification import UserNotification
from .CancellationInfo import CancellationInfo
from .ReturnInfo import ReturnInfo
from .FulfillmentInfo import FulfillmentInfo
from .InTransitInfo import InTransitInfo
from .LineItemUpdate import LineItemUpdate
from .Receipt import Receipt
from .RejectionInfo import RejectionInfo
from .Extension import Extension


class StructuredResponse(MyDict):
    """
    {
      "orderUpdate": {
        object(OrderUpdate)
      },
    }
    """
    order_update: OrderUpdate = DictProperty('orderUpdate', OrderUpdate)

    def build(self, order_update: OrderUpdate = None):
        self.order_update = order_update
        return self

    def add_order_update(self, google_order_id: str=None, action_order_id: str=None, order_state: OrderState=None,
                         order_management_actions_list: List[Action]=None, receipt: Receipt=None, update_time: str=None,
                         total_price: Price=None, line_item_updates: LineItemUpdate=None, user_notification: UserNotification=None,
                         info_extension:Extension=None, rejection_info:RejectionInfo=None, cancellation_info:CancellationInfo=None,
                         in_transit_info:InTransitInfo=None, fulfillment_info:FulfillmentInfo=None, return_info:ReturnInfo=None) -> OrderUpdate:
        self.order_update = OrderUpdate().build(google_order_id=google_order_id,action_order_id=action_order_id
                                                ,order_state=order_state,
                                                order_management_actions_list=order_management_actions_list,
                                                receipt=receipt, update_time=update_time, total_price=total_price,
                                                line_item_updates=line_item_updates, user_notification=user_notification,
                                                info_extension=info_extension,rejection_info=rejection_info,
                                                cancellation_info=cancellation_info,in_transit_info=in_transit_info,
                                                fulfillment_info=fulfillment_info,return_info=return_info)
        return self.order_update
