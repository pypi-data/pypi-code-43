from PyVoice.MyDict import MyDict, DictProperty


class FulfillmentInfo(MyDict):
    """
    {
      "deliveryTime": string,
    }
    """
    delivery_time: str = DictProperty('deliveryTime', str)
    
    def build(self, delivery_time: str=None):
        if delivery_time is not None:
            self.delivery_time = delivery_time
        return self
