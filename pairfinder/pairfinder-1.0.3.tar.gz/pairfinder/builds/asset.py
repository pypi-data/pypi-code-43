index_dic = {'KOSPI': "001", "KOSDAQ": "201", "MSCI": "530", "KOSPI200": "180"}

# Dont Forget '.'
suffix_yahoo_dic = {'US':'', 'IM':'.MI', 'DC':'.CO', 'FH':'.HE', 'BZ':'.SA', 'RM':'.ME', 'CI':'.SN',
                    'AR':'.BA', 'CN':'.TO', 'SS':'.ST', 'LN':'.L', 'MM':'.MX', 'NA':'.AS', 'SM':'.MC', 'NO':'.OL',
                    'CH':'.SS', 'GR':'.DE', 'CH':'.SS'}
st_yahoo_dic = ['SCA']


# TODO: SS:.ST? SS:.SW?

prefix_cybos_dic = {'stock':'A', 'etf':'A', 'index':'U'}

prefix_dic = {'cybos':prefix_cybos_dic}
suffix_dic = {'yahoo':suffix_yahoo_dic}

def suffix_factory(source, exchange):
    if source in suffix_dic.keys():
        if exchange in suffix_dic[source].keys():
            return '{}'.format(suffix_dic[source][exchange])
        else:
            if source == 'yahoo':
                return '.{}'.format(exchange)
    else:
        if source == 'bloomberg':
            return ' {} Equity'.format(exchange)
        else:
            return ''

class Asset:
    def __init__(self, symbol, type_, exchange='KS', source='cybos', name=None, **kwargs):
        self.symbol, self.type, self.exchange, self.source = symbol, type_, exchange, source
        self.data = {}

        if name is None:
            self.name = symbol
        else:
            self.name = name

        # Add additonal data when to initalize (Optional)
        for key, value in kwargs.items():
            exec("self.data['{}'] = '{}'".format(key, value))

        self.suffix = suffix_factory(self.source, self.exchange)
        self.prefix = prefix_dic[self.source][self.type] if self.source in prefix_dic.keys() else ''

    def use(self):
        return self.prefix + self.symbol + self.suffix

def asset_wrapper(type_):
    class ProductClass(Asset):
        def __init__(self, symbol, exchange='KS', source='cybos', name=None, **kwargs):
            if type_ == 'index' and source=='cybos':
                symbol = index_dic[symbol] if symbol in index_dic.keys() else symbol
            super().__init__(symbol=symbol, type_=type_, exchange=exchange, source=source, name=name)
            for key, value in kwargs.items():
                exec("self.data['{}'] = '{}'".format(key, value))
    return ProductClass


def asset_factory(symbol, name=None, type_='stock', exchange='KS', source='cybos'):
    if type_ == 'stock':
        return Stock(symbol=symbol, name=name, exchange=exchange, source=source)
    elif type_ == 'etf':
        return ETF(symbol=symbol, name=name, exchange=exchange, source=source)
    elif type_ == 'index':
        return Index(symbol=symbol, name=name, exchange=exchange, source=source)
    else:
        return Asset(symbol=symbol, type_=type_, name=name, exchange=exchange, source=source)


class Pair:
    def __init__(self, y_asset, x_asset, **kwargs):
        self.y_asset = y_asset
        self.x_asset = x_asset

        self.data = {}
        self.spread = {}
        self.hedge_ratio = {}
        self.intercept = {}

        # Add additonal data when to initalize (Optional)
        for key, value in kwargs.items():
            exec("self.data['{}'] = '{}'".format(key, value))

Stock = asset_wrapper(type_='stock')
ETF = asset_wrapper(type_='etf')
Index = asset_wrapper(type_='index')

def main():
    stock = asset_factory(symbol='KOSPI', type_='index', source='cybos', exchange='KS')
    print(stock.use())

if __name__ == '__main__':
    main()


