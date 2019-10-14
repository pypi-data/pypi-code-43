from ingaia.gcloud import ProjectReference, StorageUtil
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class RequestLoggerConfig:
    # constants
    DB_STORE = True
    REQUEST_LOGGER_DATA_STORE_URL = 'https://us-central1-ingaia-request-logger.cloudfunctions.net/save_request_log'

    # Google cloud constants
    GOOGLE_CLOUD_PROJECT_ID = 'ingaia-request-logger'
    GOOGLE_CLOUD_DEFAULT_LOCATION = 'southamerica-east1'
    GOOGLE_CLOUD_PROJECT = ProjectReference(GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_DEFAULT_LOCATION)

    # Authentication
    OPERATIONS_APP_CLIENT = 'ingaia_operations'  # Id from Google Firestore
    JWT_ISSUER = 'br.com.inagaia.operations'  # Name of the issuer
    JWT_LIFETIME_SECONDS = 3600  # 1 hour
    JWT_ALGORITHM = 'RS256'

    # queue configuration
    REQUEST_LOG_TOPIC_NAME = 'trace'

    RSA_BUCKET_LOCATION = 'us'
    RSA_BUCKET = 'ingaia-request-logger-rsa'
    RSA_PRIVATE_KEY = 'rl-token-key'
    RSA_PUBLIC_KEY = 'rl-token-key.pub'
    RSA_PROJECT_REF = ProjectReference(GOOGLE_CLOUD_PROJECT_ID, RSA_BUCKET_LOCATION)

    @property
    def JWT_SECRET(self):
        # configure the private key
        private_key = StorageUtil(self.RSA_BUCKET, self.RSA_PRIVATE_KEY, project=self.RSA_PROJECT_REF).get_content()
        # private_key = str(file_key).encode('utf-8')
        return load_pem_private_key(private_key, password=b'inGaia,2019', backend=default_backend())

    @classmethod
    def enable_database_store(cls):
        cls.DB_STORE = True

    @classmethod
    def disable_database_store(cls):
        cls.DB_STORE = False


config = RequestLoggerConfig()
