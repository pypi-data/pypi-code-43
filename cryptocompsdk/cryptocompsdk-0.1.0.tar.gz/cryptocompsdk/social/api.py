from typing import Sequence, Optional

from cryptocompsdk.request import APIBase
from cryptocompsdk.social.parse import SocialData, social_data_from_dict, CouldNotGetSocialException
from cryptocompsdk.urls import DAILY_SOCIAL_URL, HOURLY_SOCIAL_URL


class SocialAPI(APIBase):
    _exception_class = CouldNotGetSocialException

    def get(self, coin_id: int = 1182, freq: str = 'd',aggregate: Optional[int] = None, end_time: Optional[int] = None,
            limit: int = 100) -> SocialData:
        url = self._get_api_url_from_freq(freq)

        payload = dict(
            coinId=coin_id,
            aggregate=aggregate,
            limit=limit,
            toTs=end_time,
        )

        return super().get(url, payload)

    def _get_api_url_from_freq(self, freq: str) -> str:
        parsed_freq = freq.lower().strip()[0]
        if parsed_freq == 'd':
            return DAILY_SOCIAL_URL
        elif parsed_freq == 'h':
            return HOURLY_SOCIAL_URL
        else:
            raise ValueError(f'could not parse frequency {freq}, pass one of d, h')
        
    def _class_factory(self, data: dict):
        return social_data_from_dict(data)
