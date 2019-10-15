from sixecho import Client, Image

a = Image()
a.generate(imgpath="a.jpg")

meta_books = {
    "category_id": "1",
    "publisher_id": "1",
    "title": "follo",
    "author": "xxx"
}

a.merge_meta(meta_books)
client = Client(
    host_url=
    "https://mc64byvj0i.execute-api.ap-southeast-1.amazonaws.com/prod/",
    api_key="4S8Vps2d7t3FiYgt07lQL1i620JRR8Ena0DWhVmv",
)
client.upload('123456789theeratnon', a)
