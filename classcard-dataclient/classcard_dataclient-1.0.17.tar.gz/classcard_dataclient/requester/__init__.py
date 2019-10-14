import requests


class Requester(object):
    def __init__(self, *args, **kwargs):
        """
        Base Requester
        :param args:
        :param kwargs:
        token : Authorization
        server: "protocol://host:port" or "protocol://host"
        protocol: default http
        host: default localhost
        port: default None
        """
        token = kwargs.pop("token", None)
        server = kwargs.pop("server", None)
        headers = kwargs.pop("headers", {})
        protocol = kwargs.pop("protocol", "http")
        host = kwargs.pop("host", "localhost")
        port = kwargs.pop("port", None)
        self.token = token
        self.headers = headers
        if server:
            self.server = server
        else:
            if port:
                self.server = "{}://{}:{}".format(protocol, host, port)
            else:
                self.server = "{}://{}".format(protocol, host)

    def check_res(self, data):
        return data, True

    def _get_method(self, route, params={}, headers={}, timeout=3600):
        url = "{}{}".format(self.server, route)
        headers.update(self.headers)
        res = requests.get(url=url, headers=headers, params=params)
        try:
            res.raise_for_status()
            data = res.json()
            data, success = self.check_res(data)
        except (Exception,) as e:
            import traceback
            print("error in {}".format(url))
            print(traceback.print_exc())
            print(res.text)
            return None
        return data

    def _download_method(self, route, file_path, params={}, headers={}):
        url = "{}{}".format(self.server, route)
        headers.update(self.headers)
        res = requests.get(url=url, headers=headers, params=params, timeout=3600)
        try:
            res.raise_for_status()
            with open(file_path, "wb") as code:
                code.write(res.content)
        except (Exception,):
            print(res.text)
            return None

    def _post_method(self, route, data={}, headers={}):
        url = "{}{}".format(self.server, route)
        headers.update(self.headers)
        res = requests.post(url=url, json=data, headers=headers, timeout=3600)
        try:
            res.raise_for_status()
            print(res.text)
            data = res.json()
            data, success = self.check_res(data)
        except (Exception,):
            print(res.text)
            return None
        return data

    def _put_method(self, route, data={}, headers={}):
        url = "{}{}".format(self.server, route)
        headers.update(self.headers)
        res = requests.put(url=url, json=data, headers=headers, timeout=3600)
        try:
            res.raise_for_status()
            print(res.text)
            data = res.json()
            data, success = self.check_res(data)
        except (Exception,):
            print(res.text)
            return None
        return data

    def _delete_method(self, route, data={}, headers={}):
        url = "{}{}".format(self.server, route)
        headers.update(self.headers)
        res = requests.delete(url=url, json=data, headers=headers, timeout=3600)
        try:
            res.raise_for_status()
            print(res.text)
            data = res.json()
            data, success = self.check_res(data)
        except (Exception,):
            print(res.text)
            return None
        return data

    def _post_file_method(self, route, files, data={}, headers={}):
        url = "{}{}".format(self.server, route)
        headers.update(self.headers)
        res = requests.post(url=url, files=files, data=data, headers=headers)
        try:
            res.raise_for_status()
            data = res.json()
            data, success = self.check_res(data)
        except (Exception,):
            print(res.text)
            return None
        return data

    def wrap_key_name(self, info, key_names):
        value_list = []
        for k in key_names:
            value_list.append(str(info[k]))
        return "-".join(value_list)

    def wrap_map(self, func_name, key_names, value_name, limit=300):
        key_map = {}
        count, offset = None, 0
        while True:
            if not limit:
                res = getattr(self, func_name)()
            elif offset:
                res = getattr(self, func_name)(params={'limit': limit, 'offset': offset})
            else:
                res = getattr(self, func_name)(params={'limit': limit})
            count = res.get('count', None) if isinstance(res, dict) else res
            if count is None:
                raise AttributeError("data have no count")
            data = res.get('results', None) if isinstance(res, dict) else res
            if data is None:
                raise AttributeError("data have no results")
            for item in data:
                key_name = self.wrap_key_name(item, key_names)
                key_map[key_name] = item[value_name]
            if not limit:
                break
            offset += limit
            print(">>> Nirvana request {} already get {}/{}".format(func_name, offset, count))
            if count is not None and offset >= count:
                break
        return key_map
