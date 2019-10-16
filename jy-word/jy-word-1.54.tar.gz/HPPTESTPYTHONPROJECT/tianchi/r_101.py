# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/9/6 0006
__author__ = 'huohuo'
# import csv
# csv.register_dialect('mydialect', delimiter=' ', quoting=csv.QUOTE_ALL)
# with open('r101.txt', ) as tsvfile:
#     # file_list = csv.reader(tsvfile, 'mydialect')
#     # for line in file_list:
#     #     print line
#     lines = tsvfile.readlines()
#     for line in lines[1:]:
#         arr = line.strip().strip('\n').split('   ')
#         arr2 = []
#         for a in arr:
#             a = a.strip()
#             if a:
#                 arr2.append(int(float(a)))
#         print len(arr2)
import requests
url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=Washington,DC&destinations=New+York+City,NY&key=AIzaSyBggxnMFVnTikeNrRkEsee18g6Q2OuybpI&callback=initMap'
headers = {
    # 'Content-Type': 'application/json',
    ':authority': 'maps.googleapis.com',
    'upgrade-insecure-requests': '1',
    'cache-control': 'max-age=0',
    'x-client-data': 'CI22yQEIorbJAQjBtskBCKmdygEIqKPKAQixp8oBCOKoygEI8anKAQi4qsoBCMuuygE=',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}

# res = requests.get(url, headers=headers)
# if res.status_code == 200:
#     print res.json()
# else:
#     print res.status_code

import requests
url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
response = requests.get(url, params={
    'units': 'imperial',
    'origins': 'Washington,DC',
    'estinations': 'New+York+City,NY',
    'key': 'AIzaSyBggxnMFVnTikeNrRkEsee18g6Q2OuybpI',
    'callback': 'initMap',
})
# print response.status_code
if __name__ == "__main__":
    'sss aa     bb'.split(' ')
    pass
    

