from mongoengine.connection import connect

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    "tests",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
]

# MongoDB for data storage
# FIXME: find mock that supports gridfs
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_NAME = "test"
MONGODB_URI = "mongodb://%s:%d/%s" % (MONGO_HOST, MONGO_PORT, MONGO_NAME)
connect(MONGO_NAME, host=MONGODB_URI)
