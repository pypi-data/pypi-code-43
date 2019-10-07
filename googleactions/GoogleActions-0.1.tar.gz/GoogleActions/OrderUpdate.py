from typing import List
from PyVoice.MyDict import MyDict, DictProperty
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
from .Button import Button
from .OpenUrlAction import OpenUrlAction
from .AndroidApp import AndroidApp
from . import ActionType, PriceType, ReasonType
from .Money import Money


class OrderUpdate(MyDict):
    """
    {
      "googleOrderId": string,
      "actionOrderId": string,
      "orderState": {
        object(OrderState)
      },
      "orderManagementActions": [
        {
          object(Action)
        }
      ],
      "receipt": {
        object(Receipt)
      },
      "updateTime": string,
      "totalPrice": {
        object(Price)
      },
      "lineItemUpdates": {
        string: {
          object(LineItemUpdate)
        },
        ...
      },
      "userNotification": {
        object(UserNotification)
      },
      "infoExtension": {
        "@type": string,
        field1: ...,
        ...
      },

      // Union field info can be only one of the following:
      "rejectionInfo": {
        object(RejectionInfo)
      },
      "cancellationInfo": {
        object(CancellationInfo)
      },
      "inTransitInfo": {
        object(InTransitInfo)
      },
      "fulfillmentInfo": {
        object(FulfillmentInfo)
      },
      "returnInfo": {
        object(ReturnInfo)
      },
      // End of list of possible types for union field info.
    }
    """
    google_order_id: str = DictProperty('googleOrderId', str)
    action_order_id: str = DictProperty('actionOrderId', str)
    order_state: OrderState = DictProperty('orderState', OrderState)
    order_management_actions_list: List[Action] = DictProperty('orderManagementActions', Action)
    receipt: Receipt = DictProperty('receipt', Receipt)
    update_time: str = DictProperty('updateTime', str)
    total_price: Price = DictProperty('totalPrice', Price)
    line_item_updates: LineItemUpdate = DictProperty('lineItemUpdates', LineItemUpdate)
    user_notification: UserNotification = DictProperty('userNotification', UserNotification)
    info_extension: Extension = DictProperty('infoExtension', Extension)
    rejection_info: RejectionInfo = DictProperty('rejectionInfo', RejectionInfo)
    cancellation_info: CancellationInfo = DictProperty('cancellationInfo', CancellationInfo)
    in_transit_info: InTransitInfo = DictProperty('inTransitInfo', InTransitInfo)
    fulfillment_info: FulfillmentInfo = DictProperty('fulfillmentInfo', FulfillmentInfo)
    return_info: ReturnInfo = DictProperty('returnInfo', ReturnInfo)

    def build(self, google_order_id: str=None, action_order_id: str=None, order_state: OrderState=None,
              order_management_actions_list: List[Action]=None, receipt: Receipt=None, update_time: str=None,
              total_price: Price=None, line_item_updates: LineItemUpdate=None, user_notification: UserNotification=None,
              info_extension:Extension=None, rejection_info:RejectionInfo=None, cancellation_info:CancellationInfo=None,
              in_transit_info:InTransitInfo=None, fulfillment_info:FulfillmentInfo=None, return_info:ReturnInfo=None):

        if receipt is not None:
            self.receipt = receipt
        if info_extension is not None:
            self.info_extension = info_extension
        if return_info is not None:
            self.return_info = return_info
        if user_notification is not None:
            self.user_notification = user_notification
        if rejection_info is not None:
            self.rejection_info = rejection_info
        if update_time is not None:
            self.update_time = update_time
        if line_item_updates is not None:
            self.line_item_updates = line_item_updates
        if fulfillment_info is not None:
            self.fulfillment_info = fulfillment_info
        if total_price is not None:
            self.total_price = total_price
        if in_transit_info is not None:
            self.in_transit_info = in_transit_info
        if action_order_id is not None:
            self.action_order_id = action_order_id
        if cancellation_info is not None:
            self.cancellation_info = cancellation_info
        if order_state is not None:
            self.order_state = order_state
        if google_order_id is not None:
            self.google_order_id = google_order_id
        if order_management_actions_list is not None:
            self.order_management_actions_list = order_management_actions_list

        def return_function(key, function):
            def inner(key):
                key = function

            return inner

        setattr(self, 'add_rejection', return_function(self.rejection_info, self.rejection_info.build))

    def add_order_management_actions(self, *order_management_actions) -> List[Action]:
        for item in order_management_actions:
            assert isinstance(item, Action)
            self.order_management_actions_list.append(item)
        return self.order_management_actions_list

    def add_order_management_action(self, title: str, url: str, action_type: ActionType, android_package_name: str=None,
                                    *android_versions) -> Action:
        if android_package_name is not None:
            android_app = AndroidApp().build(package_name=android_package_name, *android_versions)
        else:
            android_app = None

        action: Action = Action().build(button=Button().build(title=title,
                                                              open_url_action=OpenUrlAction().build(url=url,
                                                                                                    android_app=android_app
                                                                                                    )
                                                              )
                                        , action_type=action_type)
        self.order_management_actions_list.append(action)
        return action

    def add_receipt(self, user_visible_order_id:str=None, confirmed_action_order_id:str=None) -> Receipt:
        self.receipt = Receipt().build(user_visible_order_id=user_visible_order_id,
                                       confirmed_action_order_id=confirmed_action_order_id)
        return self.receipt

    def add_total_price(self, price_type:PriceType, amount, currency_code) -> Price:
        self.total_price = Price().build(price_type=price_type, amount=Money().build(amount=amount,
                                                                                     currency_code=currency_code))

        return self.total_price

    def add_line_item_updates(self, reason: str, price_type:PriceType, amount:float, currency_code:str,
                              state:str, label: str, extension_type: str, **extension_kwargs) -> LineItemUpdate:
        self.line_item_updates = LineItemUpdate().build(reason=reason, price=Price().build(price_type=price_type,
                                                                                           amount=Money().build(
                                                                                               amount=amount,
                                                                                               currency_code=currency_code
                                                                                           )),
                                                        order_state=OrderState().build(state=state,label=label),
                                                        extension=Extension().build(type=extension_type,
                                                                                    **extension_kwargs))
        return self.line_item_updates

    def add_user_notification(self, text:str, title:str) -> UserNotification:
        self.user_notification = UserNotification().build(text=text, title=title)
        return self.user_notification

    def add_info_extension(self, type:str, **kwargs) -> Extension:
        self.info_extension = Extension().build(type, **kwargs)
        return self.info_extension

    def add_rejection_info(self, type:ReasonType, reason:str) -> RejectionInfo:
        self.rejection_info = RejectionInfo().build(type=type, reason=reason)
        return self.rejection_info

    def add_cancellation_info(self, reason:str) -> CancellationInfo:
        self.cancellation_info = CancellationInfo().build(reason=reason)
        return self.cancellation_info

    def add_intransit_info(self, updated_time: str) -> InTransitInfo:
        self.in_transit_info = InTransitInfo().build(updated_time=updated_time)
        return self.in_transit_info

    def add_fulfillment_info(self, delivery_time: str) -> FulfillmentInfo:
        self.fulfillment_info = FulfillmentInfo().build(delivery_time=delivery_time)
        return self.fulfillment_info

    def add_return_info(self, reason: str) -> ReturnInfo:
        self.return_info = ReturnInfo().build(reason=reason)
        return self.return_info
