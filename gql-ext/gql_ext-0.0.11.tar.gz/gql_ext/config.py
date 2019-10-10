class Config:
    REST_QUERY_TIMEOUT = 10
    DB_QUERY_TIMEOUT = 10
    databases = {}
    rest = {}
    proxy_headers = []
    default_service = None
    allow_cors = True

    class QueryCache:
        ttl = 60
        max_size = 1024

    def get_rest(self, service_name=None):
        if not service_name:
            return self.rest

        return self.rest.get(service_name)

    def get_db(self, db_name=None):
        if not db_name:
            return self.databases
        return self.databases.get(db_name)

    def set_db(self, db_name, dsn, **kwargs):
        db_conf = {**kwargs, 'dsn': dsn}
        self.databases[db_name] = db_conf

    def set_rest(self, rest, base_url):
        self.rest[rest] = base_url

    def set_proxy_headers(self, proxy_headers):
        self.proxy_headers = proxy_headers

    def set_default_service(self, service: str):
        self.default_service = service
