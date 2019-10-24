class signal:
    '''
    signal is a model for evaluating features like lagged OHLC data, fundamental data, related security information, macro data (like GDP growth, interest rate change, FX movement) to output trading recomendation. 
    The API here is much like sk-learn models if it needs to be updated or trained with new data. The model can also be hard-code rules for certain logic. The output can be a direct trade label (Buy, Sell, Hold or numerical values 1, 0, -1) or a rating for each trade label, or a probability distribution of each label.
    '''
    def __init__(self):

        pass

    
    def set_price(self, OHLC_data, start_date=None, end_date=None):
        pass

    def backtest(self, OHLC_data=None, start_date=None, end_date=None):
        pass

    def fit(self, train_data, train_label):
        pass
    
    def predict_trade(self, test_set):
        pass
    
    def predict_rating(self, test_set):
        pass
    
    def predict_prob(self, test_set):
        pass


class order:
    pass

class exchange:
    def __init_(self):
        pass 
    
    def dump_order(self, order):
        pass

    def match_order(self):
        pass 

class market:
    def __init__(self, OHLC):
        pass 
    
    def dump_order(self, order):
        pass 

    def execute_order(self):
        pass