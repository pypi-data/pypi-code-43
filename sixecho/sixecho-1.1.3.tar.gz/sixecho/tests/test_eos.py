# -*- coding: utf-8 -*-
import eospy.cleos
import pytz
from sixecho import Chain, Image


def test_eos():
    ce = eospy.cleos.Cleos(url='http://localhost:8888')

    # cleos push action hello hi '["bob"]' -p bob@active
    arguments = {"user": 'bob'}
    payload = {
        "account": "hello",
        "name": "hi",
        "authorization": [{
            "actor": "bob",
            "permission": "active",
        }],
    }

    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)

    print(data)

    payload['data'] = data['binargs']
    print(payload)
    trx = {"actions": [payload]}
    import datetime as dt
    trx['expiration'] = str(
        (dt.datetime.utcnow() +
         dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

    key = eospy.keys.EOSKey(
        '5KDA5SewCxdFBSfiLKBnmNZR7PBZ3jZbtLpPhqhwi1LZ2dAHkAu')
    print(trx)
    resp = ce.push_transaction(trx, key, broadcast=True)

    print('------------------------------------------------')
    print(resp)
    print('------------------------------------------------')


def basic_submit():
    #  cleos push action assets create  '["bob1","balls","bob1","{\"power\": 10, \"speed\": 2.2, \"name\": \"Magic Sword\" }","{\"color\": \"bluegold\", \"level\": 3, \"stamina\": 5, \"img\": \"https://bit.ly/2MYh8EA\" }",0]' -p bob1@active
    ce = eospy.cleos.Cleos(
        url='http://ec2-3-0-89-218.ap-southeast-1.compute.amazonaws.com:8888')

    arguments = {
        "author": 'bob1',
        "category": "balls",
        "owner": "bob1",
        "idata": "",
        "mdata": "",
        "requireclaim": 0
    }
    payload = {
        "account": "assets",
        "name": "create",
        "authorization": [{
            "actor": "bob1",
            "permission": "active",
        }],
    }

    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)

    #  print(data)

    payload['data'] = data['binargs']
    #  print(payload)
    trx = {"actions": [payload]}
    import datetime as dt
    trx['expiration'] = str(
        (dt.datetime.utcnow() +
         dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

    key = eospy.keys.EOSKey(
        '5KGai6RY4JL59CzY9L8whYo7gAQhmtw9DwvRTPgLJYCDyJpWbxe')
    #  print(trx)
    resp = ce.push_transaction(trx, key, broadcast=True)

    print('------------------------------------------------')
    print(resp)
    print('------------------------------------------------')


def main():
    a = Image()
    a.generate(imgpath="a.jpg")
    meta_image = {
        "category_id": "1",
        "publisher_id": "1",
        "title": "follo",
        "author": "sixecho",
        "link": "https://computerlogy.com",
        "model": a.exif["Model"]
    }
    #  a.merge_meta(meta_image)
    #  print(a.exif)
    a.set_meta(meta_image)
    sixEOS = Chain(
        private_key="5KGai6RY4JL59CzY9L8whYo7gAQhmtw9DwvRTPgLJYCDyJpWbxe",
        host_url=
        "http://ec2-3-0-89-218.ap-southeast-1.compute.amazonaws.com:8888")
    data = sixEOS.push_transaction("bob1", [{
        "actor": "bob1",
        "permission": "active",
    }], a)
    print(data)
    ce = eospy.cleos.Cleos(
        url='http://ec2-3-0-89-218.ap-southeast-1.compute.amazonaws.com:8888')
    print(ce.get_transaction(data['transaction_id']))


if __name__ == "__main__":
    main()
