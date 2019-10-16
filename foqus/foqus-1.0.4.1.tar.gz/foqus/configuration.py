import os, socket

ENABLE_LOG_TRACES = os.environ.get('ENABLE_LOG_TRACES')

INPUT_PATH = os.environ.get('INPUT_PATH')
OUTPUT_PATH = os.environ.get('OUTPUT_PATH')
VECTORS_PATH = os.environ.get('VECTORS_PATH')
STREAMS_PATH = os.environ.get('STREAMS_PATH')
TRAININGS_PATH = os.environ.get('TRAININGS_PATH')
LOG_PATH = os.environ.get('LOG_PATH')

TARGET_RESOLUTION = int(os.environ.get('TARGET_RESOLUTION'))
BATCH_SIZE = int(os.environ.get('BATCH_SIZE'))
EPOCHS = int(os.environ.get('EPOCHS'))

MAX_IMAGES_TO_VECTORIZE = int(os.environ.get('MAX_IMAGES_TO_VECTORIZE'))
MAX_SIMILARITY_RESULT_NUMBER = int(os.environ.get('MAX_SIMILARITY_RESULT_NUMBER'))
MAX_DOWNLOAD_FILE_RETRIES = int(os.environ.get('MAX_DOWNLOAD_FILE_RETRIEVES'))
MAX_ALLOWED_THREADS = int(os.environ.get('MAX_ALLOWED_THREADS'))
THREAD_RESPONSE_TIMEOUT_IN_SECONDS = float(os.environ.get('THREAD_RESPONSE_TIMEOUT_IN_SECONDS'))
USE_GPU_ACCELERATIONS = bool(os.environ.get('USE_GPU_ACCELERATIONS'))

BACKEND_VERSION = os.environ.get('BACKEND_VERSION')

MESSAGE_QUEUE_ADDRESS = os.environ.get('MESSAGEQUEUE_ADDRESS')
MESSAGE_QUEUE_PORT = os.environ.get('MESSAGEQUEUE_PORT')
MESSAGE_QUEUE_SSL = bool(os.environ.get('MESSAGEQUEUE_SSL'))
MESSAGE_QUEUE_USER = os.environ.get('MESSAGEQUEUE_USER')
MESSAGE_QUEUE_PASSWORD = os.environ.get('MESSAGEQUEUE_PASSWORD')
MESSAGE_QUEUE_HEARTBEAT_INTERVAL = int(os.environ.get('MESSAGEQUEUE_HEARTBEAT_INTERVAL'))

MESSAGE_QUEUE_INPUT_NAME = os.environ.get('MESSAGEQUEUE_INPUT_NAME')
MESSAGE_QUEUE_ENGINE_NAME = os.environ.get('MESSAGEQUEUE_ENGINE_NAME')

DATABASE_ADDRESS =os.environ.get('DATABASE_ADDRESS')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HASH_TABLE_NAME = os.environ.get('DATABASE_HASH_TABLE_NAME')
DATABASE_USERS_MANAGEMENT_TABLE_NAME = os.environ.get('DATABASE_USERS_MANAGEMENT')
DATABASE_CMS_CLIENT_TABLE_NAME= os.environ.get('CMS_CLIENT_TABLE')

AWS_KEY_ID = os.environ.get('AWS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
INPUT_S3 = os.environ.get('AWS_INPUT_PATH_S3')
OUTPUT_S3 = os.environ.get('AWS_OUTPUT_PATH_S3')
STREAMS_S3 = os.environ.get('AWS_STREAMS_PATH_S3')
VECTORS_S3 = os.environ.get('AWS_VECTORS_PATH_S3')
TRAININGS_S3 = os.environ.get('AWS_TRAINING_PATH_S3')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER_NAME = os.environ.get('AZURE_CONTAINER_NAME')
AZURE_INPUT_PATH = os.environ.get('AZURE_INPUT_PATH')
AZURE_OUTPUT_PATH = os.environ.get('AZURE_OUTPUT_PATH')
AZURE_VECTORS_PATH = os.environ.get('AZURE_VECTORS_PATH')
AZURE_STREAMS_PATH = os.environ.get('AZURE_STREAMS_PATH')
AZURE_TRAINING_PATH = os.environ.get('AZURE_TRAINING_PATH')
AZURE_TEST_IMAGES = os.environ.get('AZURE_TEST_IMAGES')
AZURE_CUSTOM_DOMAIN_BLOB = os.environ.get('AZURE_CUSTOM_DOMAIN_BLOB')


LOG_AZURE_ACCOUNT_NAME = os.environ.get('LOG_AZURE_ACCOUNT_NAME')
LOG_AZURE_ACCOUNT_KEY = os.environ.get('LOG_AZURE_ACCOUNT_KEY')


USE_AWS = bool(os.environ.get('USE_AWS'))
USE_AZURE = bool(os.environ.get('USE_AZURE'))

BASE_DIR = os.environ.get('BASE_DIR')
PATH_EMAIL_CUSTOMER = os.path.join(BASE_DIR, os.environ.get('CUSTOMER_EMAIL'))
PATH_INSCRIPTION_EMAIL_CUSTOMER = os.path.join(BASE_DIR, os.environ.get('INSCRIPTION_EMAIL'))
PATH_EMAIL_TRINING_STARTED_CMS = os.path.join(BASE_DIR, os.environ.get('EMAIL_TRINING_STARTED_CMS'))
PATH_EMAIL_TRAINING_STARTED_CUSTOMER = os.path.join(BASE_DIR, "webserver/users_management/webserverapp/templates/emails/email_of_started_training.html")
PATH_EMAIL_CLIENT_INSCRIPTION = os.path.join(BASE_DIR, "webserver/users_management/webserverapp/templates/emails/client_inscription.html")

SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SMTP_HOST = os.environ.get('SMTP_HOST')

LOCAL = bool(os.environ.get('DEV_ENV'))

DATABASE_ADDRESS_AZURE = os.environ.get('DATABASE_ADDRESS_AZURE')
DATABASE_NAME_AZURE = os.environ.get('DATABASE_NAME_AZURE')
DATABASE_USER_AZURE = os.environ.get('DATABASE_USER_AZURE')
DATABASE_PASSWORD_AZURE = os.environ.get('DATABASE_PASSWORD_AZURE')

if LOCAL:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    PROTOCOL = 'http'
    DOMAIN = PROTOCOL + '://' + ip_address + ':1234/'
    SWAGGER_CALL_ADDRESS = ip_address + ':5000'
    API_CALL_ADDRESS = PROTOCOL + '://' + ip_address + ':5000'
else:
    PROTOCOL = 'https'
    DOMAIN = os.environ.get('SERVER_DOMAIN')
    SWAGGER_CALL_ADDRESS = os.environ.get('SERVER_SWAGGER_CALL_ADDRESS')
    API_CALL_ADDRESS = os.environ.get('SERVER_API_CALL_ADDRESS')


class Config(object):
    SECRET_KEY = os.environ.get('SHOPIFY_SECRET_KEY')
    HOST = SWAGGER_CALL_ADDRESS

    SHOPIFY_CONFIG = {
        'API_KEY': os.environ.get('SHOPIFY_API_KEY'),
        'API_SECRET': os.environ.get('SHOPIFY_API_SECRET'),
        'APP_HOME': PROTOCOL + '://' + HOST,
        'CALLBACK_URL': PROTOCOL + '://' + HOST + '/install',
        'REDIRECT_URI': PROTOCOL + '://' + HOST + '/connect',
        'SCOPE': 'read_products, read_collection_listings, read_themes, write_themes, write_script_tags'
    }

# STRIPE KEY
STRIPE_PKEY = os.environ.get('STRIPE_PKEY')
STRIPE_SKEY = os.environ.get('STRIPE_SKEY')

#SECRET KEY
SECRET_KEY = os.environ.get('SECRET_KEY')
ADMIN_KEY = os.environ.get('ADMIN_KEY')

TRAINING_STEPS = int(os.environ.get('TRAINING_STEPS')) if os.environ.get('TRAINING_STEPS') else 100
USE_DATABASE_AZURE=bool(os.environ.get('USE_DATABASE_AZURE'))

SEUIL_SIMILARITY = float(os.environ.get('SEUIL_SIMILARITY'))
TIME_OUT_GET_SIMILARS = int(os.environ.get('TIME_OUT_GET_SIMILARS'))
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

# Paypal
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE')