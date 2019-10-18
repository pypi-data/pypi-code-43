from .helpers.http_client import HttpClient
from .models.lookup_result import LookupResult
from .models.keyword import Keyword
from .models.out_message import OutMessage
from .models.strex_merchant import StrexMerchant
from .models.in_message import InMessage
from .models.one_time_password import OneTimePassword
from .models.strex_transaction import StrexTransaction
from .models.public_key import PublicKey


name = "target365_sdk"


class ApiClient:
    PING = "api/ping"
    LOOKUP = "api/lookup"
    KEYWORDS = "api/keywords"
    OUT_MESSAGES = "api/out-messages"
    IN_MESSAGES = "api/in-messages"
    PREPARE_MSISDNS = "api/prepare-msisdns"
    STREX_MERCHANTS = "api/strex/merchants"
    STREX_TRANSACTIONS = "api/strex/transactions"
    STREX_ONE_TIME_PASSWORDS = "api/strex/one-time-passwords"
    SERVER_PUBLIC_KEYS = "api/server/public-keys"
    CLIENT_PUBLIC_KEYS = "api/client/public-keys"

    NOT_FOUND = 404

    def __init__(self, base_uri, key_name, private_key):
        self.client = HttpClient(base_uri, key_name, private_key)

    ###  Ping controller  ###

    def ping(self):
        """
        GET /api/ping
        Pings the service and returns a hello message
        :return: return description
        """

        response = self.client.get(self.PING)
        response.raise_for_status()

        return response.text  # returns the string "pong"

    ###  Lookup controller  ###

    def lookup(self, msisdn):
        """
        GET /api/lookup
        Looks up address info on a mobile phone number.
        :msisdn: Mobile phone number (required)
        :return: LookupResult
        """

        if msisdn is None:
            raise ValueError("msisdn")
        payload = {"msisdn": msisdn}
        response = self.client.get_with_params(self.LOOKUP, payload)
        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()

        lookup_result = LookupResult(**response.json())
        return lookup_result

    ###  Keyword controller  ###

    def create_keyword(self, keyword):
        """
        POST /api/keywords
        Creates a new keyword.
        :keyword: Keyword
        :return: string
        """
        if keyword is None:
            raise ValueError("keyword")
        response = self.client.post(self.KEYWORDS, keyword)
        response.raise_for_status()

        return self._get_id_from_header(response.headers)

    def get_all_keywords(self, short_number_id=None, keyword=None, mode=None, tag=None):
        """
        GET /api/keywords
        Gets all keywords.
        :return: Keyword[]
        """
        params = {}
        if short_number_id is not None:
            params["shortNumberId"] = short_number_id
        if keyword is not None:
            params["keywordText"] = keyword
        if mode is not None:
            params["mode"] = mode
        if tag is not None:
            params["tag"] = tag

        response = self.client.get_with_params(self.KEYWORDS, params)
        response.raise_for_status()
        return Keyword.from_list(response.json())

    def get_keyword(self, keyword_id):
        """
        GET /api/keywords/{keywordId}
        Gets a keyword.
        :keywordId: string
        :return: Keyword
        """
        if keyword_id is None:
            raise ValueError("keywordId")

        response = self.client.get(self.KEYWORDS + "/" + keyword_id)
        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()
        
        return Keyword(**response.json())

    def update_keyword(self, keyword):
        """
        PUT /api/keywords/{keywordId}
        Updates a keyword
        :param keyword: Keyword
        :return:
        """
        if keyword is None:
            raise ValueError("keyword")
        if keyword.keywordId is None:
            raise ValueError("keywordId")

        response = self.client.put(
            self.KEYWORDS + "/" + keyword.keywordId, keyword)

        response.raise_for_status()

    def delete_keyword(self, keyword_id):
        """
        DELETE /api/keywords/{keywordId}
        Deletes a keyword
        :keywordId: string
        """
        if keyword_id is None:
            raise ValueError("keywordId")

        response = self.client.delete(self.KEYWORDS + "/" + keyword_id)
        response.raise_for_status()

    ###  OutMessage controller  ###

    def prepare_msisdns(self, msisdns):
        """
        POST /api/prepare-msisdns
        MSISDNs to prepare as a string array
        :message: string[]
        """
        if msisdns is None:
            raise ValueError("msisdns")
        response = self.client.post(self.PREPARE_MSISDNS, msisdns)
        response.raise_for_status()

    def create_out_message(self, out_message):
        """
        POST /api/out-messages
        Creates a new out-message
        :message: OutMessage
        """
        if out_message is None:
            raise ValueError("message")

        response = self.client.post(self.OUT_MESSAGES, out_message)
        response.raise_for_status()

        return self._get_id_from_header(response.headers)

    def create_out_message_batch(self, out_messages):
        """
        POST /api/out-messages/batch
        Creates a new out-message batch.
        :messages: OutMessage[]
        """
        if out_messages is None:
            raise ValueError("messages")

        response = self.client.post(self.OUT_MESSAGES + "/batch", out_messages)
        response.raise_for_status()

    def get_out_message(self, transaction_id):
        """
        GET /api/out-messages/batch/{transactionId}
        Gets and out-message
        :transactionId: string
        :return: OutMessage
        """
        if transaction_id is None:
            raise ValueError("transactionId")

        response = self.client.get(self.OUT_MESSAGES + "/" + transaction_id)
        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()

        return OutMessage(**response.json())

    def update_out_message(self, out_message):
        """
        PUT /api/out-messages/batch/{transactionId}
        Updates a future scheduled out-message.
        :message: OutMessage
        """
        if out_message is None:
            raise ValueError("message")
        if out_message.transactionId is None:
            raise ValueError("transactionId")

        response = self.client.put(
            self.OUT_MESSAGES + "/" + out_message.transactionId, out_message)
        response.raise_for_status()

    def delete_out_message(self, transaction_id):
        """
        DELETE /api/out-messages/batch/{transactionId}
        Deletes a future sheduled out-message.
        :transactionId: string
        """
        if transaction_id is None:
            raise ValueError("transactionId")

        response = self.client.delete(self.OUT_MESSAGES + "/" + transaction_id)
        response.raise_for_status()

    ###  InMessages controller  ###

    def get_in_message(self, short_number_id, transaction_id):
        """
        GET /api/in-messages/{shortNumberId}/{transactionId}
        Gets and in-message
        :shortNumberId: string
        :transactionId: string
        :return: InMessage
        """
        if transaction_id is None:
            raise ValueError("transactionId")

        response = self.client.get(self.IN_MESSAGES + "/" + short_number_id + "/" + transaction_id)
        response.raise_for_status()

        return InMessage(**response.json())


    ###  StrexMerchants controller  ###

    def get_strex_merchants(self):
        """
        GET /api/strex/merchants
        Gets all merchant ids.
        :return: StrexMerchant[]
        """
        response = self.client.get(self.STREX_MERCHANTS)
        response.raise_for_status()
        return StrexMerchant.from_list(response.json())

    def get_strex_merchant(self, merchant_id):
        """
        GET /api/strex/merchants/{merchantId}
        Gets a merchant.
        :merchantId: string
        :returns: StrexMerchant
        """
        if merchant_id is None:
            raise ValueError("merchantId")

        response = self.client.get(self.STREX_MERCHANTS + "/" + merchant_id)

        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()

        return StrexMerchant(**response.json())

    def save_strex_merchant(self, strex_merchant):
        """
        PUT /api/strex/merchants/{merchantId}
        Creates/updates a merchant.
        :merchant: StrexMerchant
        """
        if strex_merchant is None:
            raise ValueError("merchant")
        if strex_merchant.merchantId is None:
            raise ValueError("merchantId")

        # expecting http 204 response (no content)
        response = self.client.put(self.STREX_MERCHANTS + "/" + strex_merchant.merchantId, strex_merchant)
        response.raise_for_status()

    def delete_strex_merchant(self, merchant_id):
        """
        DELETE /api/strex/merchants/{merchantId}
        Deletes a merchant
        :merchantId: string
        """
        if merchant_id is None:
            raise ValueError("merchantId")

        response = self.client.delete(self.STREX_MERCHANTS + "/" + merchant_id)
        response.raise_for_status()

    def create_one_time_password(self, one_time_password):
        """
        POST /api/strex/one-time-passwords
        :return:
        """

        if one_time_password is None:
            raise ValueError("invalid one_time_password")
        if one_time_password.transactionId is None:
            raise ValueError("invalid one_time_password.transactionId")
        if one_time_password.merchantId is None:
            raise ValueError("invalid one_time_password.merchantId")
        if one_time_password.recipient is None:
            raise ValueError("invalid one_time_password.recipient")
        if one_time_password.sender is None:
            raise ValueError("invalid one_time_password.sender")
        if one_time_password.recurring is None:
            raise ValueError("invalid one_time_password.recurring")

        response = self.client.post(self.STREX_ONE_TIME_PASSWORDS, one_time_password)
        response.raise_for_status()

    def get_one_time_password(self, transaction_id):
        """
        GET /api/strex/one-time-passwords/{transactionId}

        :param transaction_id:
        :return: OneTimePassword
        """

        response = self.client.get(self.STREX_ONE_TIME_PASSWORDS + '/' + transaction_id)
        response.raise_for_status()


        return OneTimePassword(**response.json())

    def create_strex_transaction(self, transaction):
        """
        POST /api/strex/transactions
        :return str:
        """

        response = self.client.post(self.STREX_TRANSACTIONS, transaction)
        response.raise_for_status()

        return self._get_id_from_header(response.headers)

    def get_strex_transaction(self, transaction_id):
        """
        GET /api/strex/transactions/{transactionId}
        :return:
        """

        response = self.client.get(self.STREX_TRANSACTIONS + '/' + transaction_id)
        response.raise_for_status()

        return StrexTransaction(**response.json())

    def delete_strex_transaction(self, transaction_id):
        """
        DELETE /api/strex/transactions/{transactionId}
        :param transaction_id:
        :return:
        """
        response = self.client.delete(self.STREX_TRANSACTIONS + '/' + transaction_id)
        response.raise_for_status()


    ### PublicKey controller  ###

    def get_server_public_key(self, key_name):
        """
        GET /api/server/public-keys/{key_name}
        :param key_name:
        :return:
        """
        response = self.client.get(self.SERVER_PUBLIC_KEYS + '/' + key_name)
        response.raise_for_status()

        return PublicKey(**response.json())

    def get_client_public_keys(self):
        """
        GET /api/client/public-keys
        :return: List
        """
        response = self.client.get(self.CLIENT_PUBLIC_KEYS)
        response.raise_for_status()

        return PublicKey.from_list(response.json())

    def get_client_public_key(self, key_name):
        """
        GET /api/client/public-keys/{key_name}
        :return: Dict
        """
        response = self.client.get(self.CLIENT_PUBLIC_KEYS + '/' + key_name)
        response.raise_for_status()

        return PublicKey(**response.json())

    def delete_client_public_key(self, key_name):
        """
        DELETE /api/client/public-keys/{key_name}
        :return:
        """
        response = self.client.delete(self.CLIENT_PUBLIC_KEYS + '/' + key_name)
        response.raise_for_status()

    # noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
    def _get_id_from_header(self, headers):
        """
        Returns the newly created resource's identifier from the Locaion header
        :returns: resource identifier
        """
        chunks = headers["Location"].split("/")
        return chunks[-1]

