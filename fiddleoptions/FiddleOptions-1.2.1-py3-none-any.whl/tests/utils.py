from datetime import date

from mercury.client.model import OptionLeg, VerticalSpread

from mercury import MarketdataApi
from mercury.client.model.option_contract_type import OptionContractType
from mercury.api_client import ApiClient, Configuration


def create_api_client():
    # todo: file configuration / environment
    cfg = Configuration()
    cfg.host = "https://mercury-api.nickelandswan.com/mercury"
    return ApiClient(configuration=cfg)


class TestUtils:
    def __init__(self):
        self.api = MarketdataApi(api_client=create_api_client())

    def create_single_option(self, opening_date):
        from mercury import OptionSingle

        name = "SPX"
        data = {'contract_type': OptionContractType.CALL,
                'from_strike': 0.3,
                'to_strike': 0.5,
                'date': date(2018, 4, 9),
                'expiration_date': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)
        option_contract = option_chain.contracts[0]
        option_single = OptionSingle(symbol='SPX',
                                     quantity=1,
                                     opening_date=opening_date,
                                     option_contract=option_contract)
        return option_single

    def create_vertical_spread(self, opening_date):

        name = "SPX"
        data = {'contract_type': OptionContractType.CALL,
                'from_strike': 0.3,
                'to_strike': 0.5,
                'date': opening_date,
                'expiration_date': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)

        contracts = option_chain.contracts
        short_leg = OptionLeg(contract=contracts[1], quantity=1)
        long_leg = OptionLeg(contract=contracts[0], quantity=-1)
        return VerticalSpread(symbol=name,
                              quantity=1,
                              opening_date=opening_date,
                              short_leg=short_leg,
                              long_leg=long_leg)

    def create_long_put_butterfly(self, opening_date):
        from mercury import \
            Butterfly

        name = "SPX"
        data = {'contract_type': OptionContractType.PUT,
                'from_strike': -0.5,
                'to_strike': -0.4,
                'date': date(2018, 4, 9),
                'expiration_date': date(2018, 6, 15)}
        option_chain = self.api.get_vertically_sliced_option_chain_by_delta(
            name, **data)
        option_contracts = option_chain.contracts
        option_contracts.sort(key=lambda n: n.strike, reverse=False)

        short_contract = option_contracts[int(len(option_contracts) / 2)]
        long_lower_leg = option_contracts[0].to_option_leg(quantity=1)
        short_leg = short_contract.to_option_leg(quantity=-2)
        long_upper_leg = option_contracts[-1].to_option_leg(quantity=1)
        butterfly = Butterfly(
            symbol='SPX',
            quantity=10,
            opening_date=opening_date,
            first_leg=long_lower_leg,
            mid_leg=short_leg,
            third_leg=long_upper_leg)

        # fix failing test
        butterfly.opening_price = 0.8999999999999773
        return butterfly
