from typing import Dict

from .base import TonglianBase


class MerchantFraudBlacklist(TonglianBase):

    def generate_biz_data(self, licenseno: str, name: str) -> Dict[str, str]:
        return {
            'licenseno': licenseno,
            'name': name,
        }


TONGLIAN_CONF = {
    "url": "https://vsp.allinpay.com/riskfeeback/customerriskqry",
    "appid": "",
    "appkey": "",
    "cusid": "",
    "version": "01",
    "randomstr": "erew3213c",  # 随机码暂无要求
    # 通联和守卫映射的code

}

if __name__ == '__main__':
    import time

    s = MerchantFraudBlacklist(TONGLIAN_CONF['url'], TONGLIAN_CONF['appkey'], TONGLIAN_CONF['appid'],
                               TONGLIAN_CONF['cusid'], TONGLIAN_CONF['version'], time.strftime('%Y%m%d%H%M%S'),
                               TONGLIAN_CONF['randomstr'])
    biz_data = s.generate_biz_data('2dew342dfda', 'sssd')
    r = s.request(biz_data)
    print(r)
