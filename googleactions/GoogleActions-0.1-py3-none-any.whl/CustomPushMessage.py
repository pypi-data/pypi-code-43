from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .Target import Target
from .OrderUpdate import OrderUpdate
from .OrderState import OrderState
from .Action import Action
from .Receipt import Receipt
from .Price import Price
from .LineItemUpdate import LineItemUpdate
from .UserNotification import UserNotification
from .RejectionInfo import RejectionInfo
from .CancellationInfo import CancellationInfo
from .InTransitInfo import InTransitInfo
from .FulfillmentInfo import FulfillmentInfo
from .ReturnInfo import ReturnInfo
from .Extension import Extension
from .Argument import Argument
from .Status import Status
from .Location import Location

class CustomPushMessage(MyDict):
    """
    {
      "target": {
        object(Target)
      },

      // Union field content can be only one of the following:
      "orderUpdate": {
        object(OrderUpdate)
      },
      "userNotification": {
        object(UserNotification)
      },
      // End of list of possible types for union field content.
    }
    """
    target: Target = DictProperty('target', Target)
    order_update: OrderUpdate = DictProperty('orderUpdate', OrderUpdate)
    user_notification: UserNotification = DictProperty('userNotification', UserNotification)

    def build(self, order_update:OrderUpdate=None, user_notification:UserNotification=None, target:Target=None):
        if order_update is not None:
            self.order_update = order_update

        if user_notification is not None:
            self.user_notification = user_notification

        if target is not None:
            self.target = target

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

    def add_user_notification(self, text:str, title:str) -> UserNotification:
        self.user_notification = UserNotification().build(text=text, title=title)
        return self.user_notification

    def add_target(self, intent=None, user_id=None, name:str=None, raw_text:str=None,
                   text_value: str=None, status:Status=None, int_value:str=None, float_value:str=None,
                   bool_value:bool=False, datetime_value:str=None, place_value: Location=None, extension:Extension=None,
                   **structure_values):

        self.target = Target().build(intent=intent, argument=Argument().build(name=name, raw_text=raw_text,
                                                                              text_value=text_value, status=status,
                                                                              int_value=int_value,
                                                                              float_value=float_value, bool_value=bool_value,
                                                                              datetime_value=datetime_value,
                                                                              place_value=place_value, extension=extension
                                                                              **structure_values),
                                     user_id=user_id)
