#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/05/08 18:56
# @Author  : niuliangtao
# @Site    : 
# @File    : ItemUtils.py
# @Software: PyCharm


import datetime
import json
import os
import sys

import numpy as np
import pandas as pd
import requests

from ..worker import decrypt

sys.path.append(os.path.dirname(__file__) + os.sep + '../')


def get_data_from_console(url):
    try:
        r = requests.get(url)
        return json.loads(r.text)
    except:
        print("error")
        return None


def get_item_detail(item_id, shop_id):
    url = decrypt(
        b'gAAAAABdaN0rQeQGj1C5L7tXMNUoocv_n6lv8mOA3fkxDHGxVhIL4h44nzkmhEGiSDZjGpkiN9-Bs68BBf0HUQ1YC2_QyF0GmtJwcvv2OHv-Mx5_by6Qjdm3p2HY_2aLV5MOpA3EaeX27u7rbwAP8ekcG_XimggIlSI8VKV4zSNBK2ZZPFAvcfI=').format(
        item_id, shop_id)

    res = None
    for i in range(0, 5):
        if res is None:
            res = get_data_from_console(url)
        else:
            break

    if res is not None:
        return res['data']
    return res


def get_data_from_dp(key='20190829100126b2d85941'):
    url = decrypt(
        b'gAAAAABdaOWVF6vzp-YMhr7qq7kceoei9h9qZPY-fEq2xsoRhuEPinuuIe4HXxXyPGWbPebcDQ9TxD0wyl_4VERjiA0-3ICDgsm0ioBw1Mym53l194xVd6csXMnGb97pcXr-_fafL_BW') + key
    headers = {
        'Authorization': decrypt(
            b'gAAAAABdaOXj-yVC-1vb6EI8quMeN3m0-VsOn2bP3TXxte5LRnKhToMCHLfhyQ2JZ1T-6t3G1VD288i3SfV1MZZkn6EPIcDYAckglfsZ9kOAykO6QbYHfqbVP0iBkD6kT64Uy87zLczJM2X7e6i9L_WWDmjeSN5ytzj_R-XRKospJxRJnY6wzqEeaTaWhMlCaY809j9_WLIE'),
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Cookie': decrypt(
            b'gAAAAABdaOXIIv42vL85GUBmjQ-PA3Psuh_gM36Sv0W54wvlrUVtQDEWzDcpafH5zJ4bvPqgZ6w1ZQID-BQPRNz3UV0apySs7o7mBKWoe-n-V1HOd59FjUxNI6WONNDWH1axENKoiex6sxVWsum9fko4TucyCSwkelKChOO6MRr-T3V0DfmMChZGF6h2gIBCHHislI7U7byEZ_s_-MEAA8Si2AKmDWB6YiId15SPNd5bLnqUuTP1vbUN4Khqtj_XRz5gzPVMXEfylqdtAVfPXzbIG8GKPj7_79MCt6VyKI2QHSizjSmIvsMI1p4RhkAeGmV9dwSrg0VWCuJPbfds9fTYX9co2yAhxsHBr_q5O28dHeuhQS30Ew7n4_ZUw9iB3GaCeNReR1nOAamLEpKPiCmuvroUOi-bnfzTfNgUr1NlkeNv-e2RBXSJH27FnnqmAfB0qM9mtdW0ds6AXXaYsu9BR4mFlEkYS3wqeIvc8cqJhKIL6genU7DRXfCJDbQoxlG8gVdIbQbBj-SspA7wVAROB5hjhsMQhZ6ZOSM9OxSqbCYWDPBGp_o1pT5yE1z0jCcZEykO7YMacihjdi4kAN2aFzLH9K3LQpvJMaUbqnOuCjo8SG2Mlv0XF-RwCSebvJXABNa9o5P8zC9uQgfYcCwP76T2XLkQEmY33nowFYZTp1A8PlTA9hQ0toeVgApAs9gQ3eq23w5RpcfaNFOnvR6BkV8w8jXmjjnuJLYBBvwK82UYZV6crZKZDEM19UAed1QQD2fZDXxXGDFT6zenTMi8qZqQxzjpAmMreRxI3xhtpaw24Q46xs1wBP9-LctksGCkp6QzahBvVkoFtfYKR9Wlc9yHBWuRyIpzGJtGZguEAfBXu2PBhsBpHmlDbSqU0S-m-jrE_LouwRJH9wCQuuLIX3_ZeGzRAQKv2Ef00q377Ge9FhhqQyZ6_vKMxvpO9XxUAh_D3HqCf-t0zGsIsMlZDXzJcWj2nEwHzNHLcE_tC_Gx3YBfIdr52tIFpAcS5Fa_g6P7dmqClky5HQKwffJQIZ6OL3tufhjEdzrYC2UG27VlYzsVCDS7Hl8W5ztc42WhbIocUh0baSbtECRZBZS-5j1lDVP1Zr9D9SuVMXgAQ2X1E_y8VG7R3fOPYWDbop703t7Bd9oobmyqrlWVqI6Tf0C3BSrAPEWJcgHi0P3Rhn4emZufa6ebeqmGwApNcgZhCayruLaM66Hsk1G9Cvkf0nkaOrHl7y5dI-S119cscpsdCBpWiMeJ_TD7IUbNVBRDacyTte3AYTCX6ReVqtl-3n7_LtK6VBdRtV_9cDO-pzWaJm-GWARq_LZcdhoK5dNnZrCXP1eH1zirwTLKOYNp93iJEtpRMpeC53zb0yrKFjZuKDeA3obsXpSzWhbBK3GD9RNdINO-P8_ByDI-P4tSAlmHn7fRaQD8wXEpVl27xKmCVoCePm78qPYE-MUUydDTrXee2nbItaR0iqFh0V0pZ-_iEdhTfsmWVYNLPmCY-5YQRweNYyqGQ4C38Vl9tYFCHBWG2fSd0zsGnPvnGzXTo_R30MMZUVaaG8OFlya1gsOQbTS0r5CjQWGgF4qYCE-8yWolDYjlqVY1P8CmYxG2Zcf8LzGOUTjGukr1wE4X56Q7cfCdXWOg-k_Oz37-tlSiXTGT4zYzfWUf2KJnrDqqLkyxCIV9zF9ZqZTHSPmrJtiAjHlU8nWGmEMGaOnzwfblmu_mnjhf0SX8YeBiElKe8a_4qEnaTsJFI8EgFB8us3WJU6rUJ3nnXPRFURT_racSyjbjKKANQE8xQlZqd9sRI2WoNjaXStsC72xXEY_6gXcJkVN40Xm9uR4VpGdZJWdd-kcR510GbvS9fqagghXhw8QedItjfxCODQEoHI2z48se75f5WbgRU3BBm5w0V4psS4cB2NqwEajLLALVMuelttMggQPUlEUNKjyXffOrpPxNtdLX3DvA3T-nKx257CiMuiZjOBJwswpC4YgNtJxi6dOHnQ-xTjv5J6NXRT55Ooxh_hkaRc6SjQQebYpfb-Wed5g8JgdPU-RvlGECybWS9IL3GKXygxDiEe0ezIAlEjpqBYue54A4m4KvJd4V097tz9Zv35rrI5Ylid8hpTtvC05XkC47-32rQQNfseBB61XVw69KN-wCIc-u30Akt2s5J9JE8wCZSPuxdTTOKERMO99k-qN_QhA4Sm-B_ZDiMX3x3JaG61u7kEw7BaV9V-WcCz49gCqhw57klXVmXMK-Y0ZK8g_x7w==')
    }

    r = requests.get(url, headers=headers)

    data = r.text
    data = json.loads(data)

    if not data['data']['completed']:
        return "not ready"

    cols = []
    types = []
    for col in data['data']['metaData']:
        # print(col)
        cols.append(col['columnName'])
        types.append(col['columnType'])

    df = pd.DataFrame(data['data']['queryResult'], columns=cols)

    for i in range(0, len(types)):
        if types[i] == 'bigint':
            df[cols[i]] = df[cols[i]].astype(np.int64)
        elif types[i] == 'float':
            df[cols[i]] = df[cols[i]].astype(np.float64)

    return df


def get_day(day=1, fm='%Y%m%d'):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=day)
    return yesterday.strftime(fm)


def test1():
    res = get_item_detail(item_id="466973942", shop_id="1206788")

    print(res)


def test2():
    day1 = get_day()
    print(day1)

    df = get_data_from_dp()
    print(df.dtypes)
