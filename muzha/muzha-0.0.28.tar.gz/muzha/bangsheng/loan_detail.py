from .base import BangShengBase


class LoanDetail(BangShengBase):
    uri = '/v1/person/loan/request-detail/t2'


# if __name__ == '__main__':
#     conf = {
#         "url": "https://bsapi.bsfit.com.cn",
#         "app_key": "",
#         "app_secret": "",
#     }
#     biz_data = {
#         'idCard': '',
#         'name': '',
#         'mobile': '',
#     }
#     loan = LoanDetail(conf['url'], LoanDetail.uri, conf['app_key'], conf['app_secret'])
#     url = loan.generate_full_url(biz_data)
#     header = loan.generate_header(biz_data)
#     r = loan.request(url, header)
#     print(r.context)
