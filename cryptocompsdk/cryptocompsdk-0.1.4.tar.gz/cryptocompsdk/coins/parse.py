from typing import Optional, Any, Dict, Union, List

import pandas as pd

from cryptocompsdk.general.parse import from_int, from_none, from_union, from_float, from_str, to_float, from_bool, \
    from_dict, to_class, is_type, from_int_or_str, from_na, from_str_number
from cryptocompsdk.response import ResponseAPIBase, ResponseException


class Taxonomy:
    access: Optional[str]
    fca: Optional[str]
    finma: Optional[str]
    industry: Optional[str]
    collateralized_asset: Optional[str]
    collateralized_asset_type: Optional[str]
    collateral_type: Optional[str]
    collateral_info: Optional[str]

    def __init__(self, access: Optional[str], fca: Optional[str], finma: Optional[str], industry: Optional[str],
                 collateralized_asset: Optional[str], collateralized_asset_type: Optional[str],
                 collateral_type: Optional[str], collateral_info: Optional[str]) -> None:
        self.access = access
        self.fca = fca
        self.finma = finma
        self.industry = industry
        self.collateralized_asset = collateralized_asset
        self.collateralized_asset_type = collateralized_asset_type
        self.collateral_type = collateral_type
        self.collateral_info = collateral_info

    @staticmethod
    def from_dict(obj: Any) -> 'Taxonomy':
        assert isinstance(obj, dict)
        access = from_union([from_str, from_none], obj.get("Access"))
        fca = from_union([from_str, from_none], obj.get("FCA"))
        finma = from_union([from_str, from_none], obj.get("FINMA"))
        industry = from_union([from_str, from_none], obj.get("Industry"))
        collateralized_asset = from_union([from_str, from_none], obj.get("CollateralizedAsset"))
        collateralized_asset_type = from_union([from_str, from_none], obj.get("CollateralizedAssetType"))
        collateral_type = from_union([from_str, from_none], obj.get("CollateralType"))
        collateral_info = from_union([from_str, from_none], obj.get("CollateralInfo"))
        return Taxonomy(access, fca, finma, industry, collateralized_asset, collateralized_asset_type, collateral_type,
                        collateral_info)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Access"] = from_union([from_str, from_none], self.access)
        result["FCA"] = from_union([from_str, from_none], self.fca)
        result["FINMA"] = from_union([from_str, from_none], self.finma)
        result["Industry"] = from_union([from_str, from_none], self.industry)
        result["CollateralizedAsset"] = from_union([from_str, from_none], self.collateralized_asset)
        result["CollateralizedAssetType"] = from_union([from_str, from_none], self.collateralized_asset_type)
        result["CollateralType"] = from_union([from_str, from_none], self.collateral_type)
        result["CollateralInfo"] = from_union([from_str, from_none], self.collateral_info)
        return result


class Coin:
    id: Optional[int]
    url: Optional[str]
    image_url: Optional[str]
    content_created_on: Optional[int]
    name: Optional[str]
    symbol: Optional[str]
    coin_name: Optional[str]
    full_name: Optional[str]
    algorithm: Optional[str]
    proof_type: Optional[str]
    fully_premined: Optional[int]
    total_coin_supply: Optional[Union[int, str]]
    built_on: Optional[str]
    smart_contract_address: Optional[str]
    pre_mined_value: Optional[str]
    total_coins_free_float: Optional[str]
    sort_order: Optional[int]
    sponsored: Optional[bool]
    taxonomy: Optional[Taxonomy]
    is_trading: Optional[bool]
    total_coins_mined: Optional[float]
    block_number: Optional[int]
    net_hashes_per_second: Optional[float]
    block_reward: Optional[float]
    block_time: Optional[int]

    def __init__(self, id: Optional[int], url: Optional[str], image_url: Optional[str],
                 content_created_on: Optional[int], name: Optional[str], symbol: Optional[str],
                 coin_name: Optional[str], full_name: Optional[str], algorithm: Optional[str],
                 proof_type: Optional[str], fully_premined: Optional[int], total_coin_supply: Optional[int],
                 built_on: Optional[str], smart_contract_address: Optional[str], pre_mined_value: Optional[str],
                 total_coins_free_float: Optional[str], sort_order: Optional[int], sponsored: Optional[bool],
                 taxonomy: Optional[Taxonomy], is_trading: Optional[bool], total_coins_mined: Optional[float],
                 block_number: Optional[int], net_hashes_per_second: Optional[float], block_reward: Optional[float],
                 block_time: Optional[int]) -> None:
        self.id = id
        self.url = url
        self.image_url = image_url
        self.content_created_on = content_created_on
        self.name = name
        self.symbol = symbol
        self.coin_name = coin_name
        self.full_name = full_name
        self.algorithm = algorithm
        self.proof_type = proof_type
        self.fully_premined = fully_premined
        self.total_coin_supply = total_coin_supply
        self.built_on = built_on
        self.smart_contract_address = smart_contract_address
        self.pre_mined_value = pre_mined_value
        self.total_coins_free_float = total_coins_free_float
        self.sort_order = sort_order
        self.sponsored = sponsored
        self.taxonomy = taxonomy
        self.is_trading = is_trading
        self.total_coins_mined = total_coins_mined
        self.block_number = block_number
        self.net_hashes_per_second = net_hashes_per_second
        self.block_reward = block_reward
        self.block_time = block_time

    @staticmethod
    def from_dict(obj: Any) -> 'Coin':
        assert isinstance(obj, dict)
        id = from_union([from_none, lambda x: int(from_str(x))], obj.get("Id"))
        url = from_union([from_str, from_none], obj.get("Url"))
        image_url = from_union([from_str, from_none], obj.get("ImageUrl"))
        content_created_on = from_union([from_int, from_none], obj.get("ContentCreatedOn"))
        name = from_union([from_str, from_none], obj.get("Name"))
        symbol = from_union([from_str, from_none], obj.get("Symbol"))
        coin_name = from_union([from_str, from_none], obj.get("CoinName"))
        full_name = from_union([from_str, from_none], obj.get("FullName"))
        algorithm = from_union([from_str, from_none], obj.get("Algorithm"))
        proof_type = from_union([from_str, from_none], obj.get("ProofType"))
        fully_premined = from_union([from_none, lambda x: int(from_str(x))], obj.get("FullyPremined"))
        total_coin_supply = from_union([from_none, from_na, from_str_number, from_int, from_float], obj.get("TotalCoinSupply"))
        built_on = from_union([from_str, from_none], obj.get("BuiltOn"))
        smart_contract_address = from_union([from_str, from_none], obj.get("SmartContractAddress"))
        pre_mined_value = from_union([from_str, from_none], obj.get("PreMinedValue"))
        total_coins_free_float = from_union([from_str, from_none], obj.get("TotalCoinsFreeFloat"))
        sort_order = from_union([from_none, lambda x: int(from_str(x))], obj.get("SortOrder"))
        sponsored = from_union([from_bool, from_none], obj.get("Sponsored"))
        taxonomy = from_union([Taxonomy.from_dict, from_none], obj.get("Taxonomy"))
        is_trading = from_union([from_bool, from_none], obj.get("IsTrading"))
        total_coins_mined = from_union([from_float, from_none], obj.get("TotalCoinsMined"))
        block_number = from_union([from_int, from_none], obj.get("BlockNumber"))
        net_hashes_per_second = from_union([from_float, from_none], obj.get("NetHashesPerSecond"))
        block_reward = from_union([from_float, from_none], obj.get("BlockReward"))
        block_time = from_union([from_int, from_none], obj.get("BlockTime"))
        return Coin(id, url, image_url, content_created_on, name, symbol, coin_name, full_name, algorithm, proof_type,
                    fully_premined, total_coin_supply, built_on, smart_contract_address, pre_mined_value,
                    total_coins_free_float, sort_order, sponsored, taxonomy, is_trading, total_coins_mined,
                    block_number, net_hashes_per_second, block_reward, block_time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Id"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                   lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.id)
        result["Url"] = from_union([from_str, from_none], self.url)
        result["ImageUrl"] = from_union([from_str, from_none], self.image_url)
        result["ContentCreatedOn"] = from_union([from_int, from_none], self.content_created_on)
        result["Name"] = from_union([from_str, from_none], self.name)
        result["Symbol"] = from_union([from_str, from_none], self.symbol)
        result["CoinName"] = from_union([from_str, from_none], self.coin_name)
        result["FullName"] = from_union([from_str, from_none], self.full_name)
        result["Algorithm"] = from_union([from_str, from_none], self.algorithm)
        result["ProofType"] = from_union([from_str, from_none], self.proof_type)
        result["FullyPremined"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                              lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                             self.fully_premined)
        result["TotalCoinSupply"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                                from_int,
                                                from_float],
                                               self.total_coin_supply)
        result["BuiltOn"] = from_union([from_str, from_none], self.built_on)
        result["SmartContractAddress"] = from_union([from_str, from_none], self.smart_contract_address)
        result["PreMinedValue"] = from_union([from_str, from_none], self.pre_mined_value)
        result["TotalCoinsFreeFloat"] = from_union([from_str, from_none], self.total_coins_free_float)
        result["SortOrder"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                          lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                         self.sort_order)
        result["Sponsored"] = from_union([from_bool, from_none], self.sponsored)
        result["Taxonomy"] = from_union([lambda x: to_class(Taxonomy, x), from_none], self.taxonomy)
        result["IsTrading"] = from_union([from_bool, from_none], self.is_trading)
        result["TotalCoinsMined"] = from_union([to_float, from_none], self.total_coins_mined)
        result["BlockNumber"] = from_union([from_int, from_none], self.block_number)
        result["NetHashesPerSecond"] = from_union([to_float, from_none], self.net_hashes_per_second)
        result["BlockReward"] = from_union([to_float, from_none], self.block_reward)
        result["BlockTime"] = from_union([from_int, from_none], self.block_time)
        return result


class RateLimit:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'RateLimit':
        assert isinstance(obj, dict)
        return RateLimit()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


class Coins(ResponseAPIBase):
    response: Optional[str]
    message: Optional[str]
    data: Optional[Dict[str, Coin]]
    base_image_url: Optional[str]
    base_link_url: Optional[str]
    rate_limit: Optional[RateLimit]
    has_warning: Optional[bool]
    type: Optional[int]

    def __init__(self, response: Optional[str], message: Optional[str], data: Optional[Dict[str, Coin]],
                 base_image_url: Optional[str], base_link_url: Optional[str], rate_limit: Optional[RateLimit],
                 has_warning: Optional[bool], type: Optional[int]) -> None:
        self.response = response
        self.message = message
        self.data = data
        self.base_image_url = base_image_url
        self.base_link_url = base_link_url
        self.rate_limit = rate_limit
        self.has_warning = has_warning
        self.type = type

    @staticmethod
    def from_dict(obj: Any) -> 'Coins':
        assert isinstance(obj, dict)
        response = from_union([from_str, from_none], obj.get("Response"))
        message = from_union([from_str, from_none], obj.get("Message"))
        data = from_union([lambda x: from_dict(Coin.from_dict, x), from_none], obj.get("Data"))
        base_image_url = from_union([from_str, from_none], obj.get("BaseImageUrl"))
        base_link_url = from_union([from_str, from_none], obj.get("BaseLinkUrl"))
        rate_limit = from_union([RateLimit.from_dict, from_none], obj.get("RateLimit"))
        has_warning = from_union([from_bool, from_none], obj.get("HasWarning"))
        type = from_union([from_int, from_none], obj.get("Type"))
        return Coins(response, message, data, base_image_url, base_link_url, rate_limit, has_warning, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Response"] = from_union([from_str, from_none], self.response)
        result["Message"] = from_union([from_str, from_none], self.message)
        result["Data"] = from_union([lambda x: from_dict(lambda x: to_class(Coin, x), x), from_none], self.data)
        result["BaseImageUrl"] = from_union([from_str, from_none], self.base_image_url)
        result["BaseLinkUrl"] = from_union([from_str, from_none], self.base_link_url)
        result["RateLimit"] = from_union([lambda x: to_class(RateLimit, x), from_none], self.rate_limit)
        result["HasWarning"] = from_union([from_bool, from_none], self.has_warning)
        result["Type"] = from_union([from_int, from_none], self.type)
        return result

    @property
    def symbol_list(self) -> List[str]:
        return [symbol for symbol in self.data]

    @property
    def symbol_id_dict(self) -> Dict[str, int]:
        return {symbol: coin.id for symbol, coin in self.data.items()}

    def to_df(self) -> pd.DataFrame:
        coin_dicts = []
        for coin_name, coin in self.data.items():
            coin_dict = coin.to_dict()
            taxonomy_dict = coin_dict.pop('Taxonomy')
            coin_dict.update(taxonomy_dict)
            coin_dicts.append(coin_dict)
        df = pd.DataFrame(coin_dicts)
        return df

def coins_from_dict(s: Any) -> Coins:
    return Coins.from_dict(s)


def coins_to_dict(x: Coins) -> Any:
    return to_class(Coins, x)


class CouldNotGetCoinsException(ResponseException):
    pass
