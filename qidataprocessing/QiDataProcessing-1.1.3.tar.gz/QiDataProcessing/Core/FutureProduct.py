class FutureProduct:
    def __init__(self, product_id="", product_name="", exchange_id=""):
        self._product_id = product_id
        self._product_name = product_name
        self._exchange_id = exchange_id
        self._all_slice = []

    @property
    def product_id(self):
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    @property
    def product_name(self):
        return self._product_name

    @product_name.setter
    def product_name(self, value):
        self._product_name = value

    @property
    def exchange_id(self):
        return self._exchange_id

    @exchange_id.setter
    def exchange_id(self, value):
        self._exchange_id = value

    @property
    def all_slice(self):
        return self._all_slice

    def init(self, product):
        self._product_id = product.product_id
        self._product_name = product.product_name
        self._exchange_id = product.exchange_id
        self._all_slice.append(product.all_slice)

    def to_string(self):
        string_builder = self._product_id
        string_builder += ("[" + self._product_name + "]")
        string_builder += "交易所=" + self._exchange_id

        return string_builder
