import eospy.cleos
import pytz
from sixecho import Chain, Image, Text

meta_books = {
    "category_id": "1",
    "publisher_id": "1",
    "title": "100 คมธรรม พุทธทาสภิกขุ-2",
    "author": "บัญชา เฉลิมชัยกิจ",
    "country_of_origin": "THA",
    "language": "th",
    "paperback": "307",
    "publish_date": 1565252419
}


def main():
    a = Text()
    a.generate(txtpath="sample.txt")
    meta_image = {
        "category_id": "1",
        "publisher_id": "1",
        "title": "100 คมธรรม พุทธทาสภิกขุ-2",
        "author": "บัญชา เฉลิมชัยกิจ",
        "country_of_origin": "THA",
        "language": "th",
        "paperback": "307",
        "publish_date": 1565252419
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
    #  ce = eospy.cleos.Cleos(
    #  url='http://ec2-3-0-89-218.ap-southeast-1.compute.amazonaws.com:8888')
    #  print(ce.get_transaction(data['transaction_id']))


if __name__ == "__main__":
    main()
