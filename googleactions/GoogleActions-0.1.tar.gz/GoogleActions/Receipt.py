from PyVoice.MyDict import MyDict, DictProperty


class Receipt(MyDict):
    """
    {
      "confirmedActionOrderId": string,
      "userVisibleOrderId": string,
    }
    """
    confirmed_action_order_id: str = DictProperty('confirmedActionOrderId', str)
    user_visible_order_id: str = DictProperty('userVisibleOrderId', str)

    def build(self, user_visible_order_id: str=None, confirmed_action_order_id: str=None):
        if user_visible_order_id is not None:
            self.user_visible_order_id = user_visible_order_id

        if confirmed_action_order_id is not None:
            self.confirmed_action_order_id = confirmed_action_order_id

        return self