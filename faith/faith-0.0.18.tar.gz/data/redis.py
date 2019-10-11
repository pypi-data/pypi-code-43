from redis import StrictRedis


redis = StrictRedis(
    host='localhost',
    port='7001',
    db='0',
)
