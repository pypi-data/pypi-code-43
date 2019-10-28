"""Veracity api library."""
__version__ = "0.1.2"

import hashlib
import json
import os.path
import requests


DEFAULT_HOST = "https://dashboard.veracity.ai/"


def paginated(f, *args, **kwargs):
	p = 1
	while True:
		items, err = f(*args, **kwargs, page=p)
		if err:
			raise Exception(err)
		l = len(items)
		if l == 0:
			break
		for item in items:
			yield item
		p = p + 1


def boolean_return(resp):
	if resp.ok:
		return True, None,
	else:
		return False, resp


class AbstractResponse():
	def as_exception(self):
		return Exception(self.data)


class LocalResponse(AbstractResponse):
	def __init__(self, data, ok=True):
		self.ok = ok
		self.resp = None
		self.data = data


class RawResponse(AbstractResponse):
	def __init__(self, resp):
		self.ok = False
		self.resp = resp
		self.data = resp.text
		if resp.status_code == 200:
			self.ok = True


class JSONResponse(AbstractResponse):
	def __init__(self, resp):
		self.ok = False
		self.resp = resp
		self.data = None
		if resp.status_code == 200:
			data = resp.json()
			if data.get("success"):
				self.ok = True
				self.data = data.get("response")
			else:
				self.data = data.get("explanation")
		else:
			self.data = resp.text

	def __repr__(self):
		return "<Response {}>".format(self.resp.status_code)


class CacheJSONResponse(AbstractResponse):
	def __init__(self, data):
		self.ok = True
		self.data = data
		self.resp = None


class Item():
	def __init__(self, client, data=None, parent=None):
		self.client = client
		self.raw = data
		self.data = self.process_input(data)
		self.parent = parent

	def process_input(self):
		raise NotImplemented()

	def _get_pk(self):
		return self.data.get("pk")

	def __repr__(self):
		return "<{} {}>".format(type(self).__name__, self._get_pk())


class Resource():
	def __init__(self, client, parent=None):
		self.client = client
		self.parent = parent


class ScreenshotUrl(Item):
	def process_input(self, data):
		return data

	def get_screenshot(self):
		print(self.data)
		resp = requests.get(self.data)
		if resp.status_code == 200:
			print("screenshot is 200")
			return resp.content, None
		else:
			return None, Exception(resp.text)


class MetadataType:
	Whois = "whois"
	Adstxt = "adstxt"
	ATSGlobal = "atsglobal"
	BuiltwithFree = "builtwithfree"
	BuiltwithDomain = "builtwithdomain"
	HTTPS = "https"
	Robotstxt = "robotstxt"
	HomepageScreenshot = "homepage_screenshot"
	HeaderBidding = "header_bidding"


class Metadata(Resource):
	def get(self, metadatatype):
		params = {
			"pk": self.parent.data["pk"],
			"metadata": metadatatype,
		}
		resp = self.client.perform_get("api/v1/domain/metadata/", params=params)
		if resp.ok:
			return resp.data, None
		else:
			return None, resp


class ArticleContent(Item):
	def process_input(self, data):
		return data

	def get_text(self):
		resp = self.client.get_text(self)
		if resp.ok:
			return resp, None
		else:
			return None, resp

	def get_raw(self):
		resp = self.client.get_raw(self)
		if resp.ok:
			return resp, None
		else:
			return None, resp


class ArticleContents(Resource):
	def get_latest(self):
		pk = self.parent.data.get("pk")
		params = {"pk": int(pk)}
		resp = self.client.perform_get("api/v1/article/latest_crawl/", params=params)
		if resp.ok:
			return ArticleContent(self.client, resp.data, self.parent), None
		else:
			return None, resp


class Article(Item):
	def process_input(self, data):
		self.contents = ArticleContents(self.client, self)
		return data


class BareArticle(Article):
	def resolve(self):
		pass


class Articles(Resource):
	def get(self, pk, fetch=True):
		params = {"pk": pk}
		if fetch == False:
			return Article(self.client, params), None
		resp = self.client.perform_get("api/v1/article/info/", params=params)
		if resp.ok:
			return Article(self.client, resp.data), None
		else:
			return None, resp


class Domain(Item):
	def process_input(self, data):
		self.metadata = Metadata(self.client, self)
		return data

	def get_screenshoturl(self):
		pk = self.data.get("pk")
		params = {"pk": pk}
		resp = self.client.perform_get("api/v1/domain/screenshot/", params=params)
		if resp.ok:
			return ScreenshotUrl(self.client, resp.data), None
		else:
			return None, resp


class BareDomain(Domain):
	def resolve(self):
		pk = self.data.get("pk")
		params = {"pk": pk}
		resp = self.client.perform_get("api/v1/domain/info/", params=params)
		if resp.ok:
			return Domain(self.client, resp.data), None
		else:
			return None, resp


class Domains(Resource):
	def get(self, pk, fetch=True):
		params = {"pk": pk}
		if fetch == False:
			return Domain(self.client, params), None
		resp = self.client.perform_get("api/v1/domain/info/", params=params)
		if resp.ok:
			return Domain(self.client, resp.data), None
		else:
			return None, resp

	def search(self, name):
		params = {"q": name}
		resp = self.client.perform_get("api/v1/domain/search/", params=params)
		if resp.ok:
			return [BareDomain(self.client, data) for data in resp.data], None
		else:
			return None, resp


datatype_to_itemcls = {
	"domain": BareDomain,
	"article": BareArticle,
}

class Tag(Item):
	def process_input(self, data):
		return data

	def get(self, obj):
		return self.get_by_pk(obj.data["pk"])

	def update(self, description):
		params = {
			"namespace": self.data["namespace"],
		}
		data = {
			"description": description,
		}
		resp = self.client.perform_post("api/v1/tag/update/", params=params, data=data)
		if resp.ok:
			return Tag(self.client, resp.data), None
		else:
			return None, resp

	def get_by_pk(self, pk):
		params = {
			"namespace": self.data["namespace"],
			"source": pk,
		}
		resp = self.client.perform_get("api/v1/tag/get/", params=params)
		return boolean_return(resp)

	def set(self, obj, value=None, values=None):
		return self.set_by_pk(obj.data["pk"], value, values)

	def set_by_pk(self, pk, value=None, values=None):
		params = {
			"namespace": self.data["namespace"],
			"source": pk,
		}
		if values is not None:
			data = {
				"values": values,
			}
		else:
			data = {
				"value": value,
			}
		resp = self.client.perform_post("api/v1/tag/set/", params=params, data=data)
		return boolean_return(resp)

	def _get_pk(self):
		return self.data.get("public_namespace", self.data["namespace"])

	def search_by_value(self, value, limit=100, page=1):
		namespace = self._get_pk()
		params = {
			"namespace": namespace,
			"value": value,
			"limit": limit,
			"page": page,
		}
		resp = self.client.perform_get("api/v1/tag/tagged/", params=params)
		cls = datatype_to_itemcls.get(self.data["source_type"])
		if resp.ok:
			return [cls(self.client, data) for data in resp.data], None
		else:
			return None, resp


class TagModel:
	Domain = "domain"
	Article = "article"
	Content = "content"


class TagType:
	String = "String"
	Integer = "Integer"
	Boolean = "Boolean"
	Array = "Array"


class Tags(Resource):
	@staticmethod
	def check_types(source_type, datatype):
		if source_type not in {"domain", "article", "content"}:
			raise Exception("unsupported model")
		if datatype not in {"String", "Integer", "Boolean", "Array"}:
			raise Exception("unsupported tagtype")

	def get(self, namespace, fetch=True, **kwargs):
		if fetch == False:
			source_type = kwargs.get("source_type")
			datatype = kwargs.get("datatype")
			try:
				Tags.check_types(source_type, datatype)
			except Exception as e:
				return None, e
			return Tag(self.client, {"namespace": namespace, "datatype": datatype, "source_type": source_type}), None
		params = {"namespace": namespace}
		resp = self.client.perform_get("api/v1/tag/", params=params)
		if resp.ok:
			return Tag(self.client, resp.data), None
		else:
			return None, resp

	def create(self, namespace, model, tagtype, description=None):
		try:
			Tags.check_types(model, tagtype)
		except Exception as e:
			return None, e
		data = {
			"namespace": namespace,
			"model": model,
			"type": tagtype,
			"description": description,
		}
		resp = self.client.perform_post("api/v1/tag/create/", data=data)
		if resp.ok:
			return Tag(self.client, resp.data), None
		else:
			return None, resp


class ContentFSResolver():
	def __init__(self, pathname):
		self.pathname = pathname

	def get(self, articlecontent):
		pk = articlecontent.data.get("pk")
		path = os.path.join(self.pathname, pk[0:2], pk[2:4], pk)
		try:
			with open(path, "r") as fh:
				content = fh.read()
		except Exception as e:
			return LocalResponse("error with {}".format(path), ok=False)
		else:
			return LocalResponse(content)


class ContentAPIResolver():
	def __init__(self, client, path):
		self.client = client
		self.path = path

	def get(self, articlecontent):
		params = {
			"pk": str(articlecontent.parent.data.get("pk")),
			"wrap": False,
		}
		resp = self.client.perform_get(self.path, params=params, json=False)
		return resp


class SimpleCache():
	def __init__(self, root, hasher=hashlib.md5):
		self.root = root
		self.hasher = hasher
		if not os.path.isdir(self.root):
			raise Exception("Cache directory does not exist")

	def make_hash(self, url, data, params):
		s = json.dumps([
			url,
			sorted(data.items()) if data else "",
			sorted(params.items()) if params else "",
		])
		h = self.hasher(s.encode("utf-8")).hexdigest()
		return os.path.join(self.root, h)

	def get(self, url, data, params):
		fn = self.make_hash(url, data, params)
		if os.path.exists(fn):
			with open(fn, "r") as fh:
				data = json.load(fh)
				return CacheJSONResponse(data)
		return None

	def set(self, url, data, params, resp):
		fn = self.make_hash(url, data, params)
		if not os.path.exists(fn):
			with open(fn, "w") as fh:
				json.dump(resp.data, fh)


class Client():
	def __init__(self, key, secret, host=DEFAULT_HOST, resolvers=None, cache=None):
		self._auth = (key, secret)
		self.host = host
		self.domains = Domains(self)
		self.articles = Articles(self)
		self.tags = Tags(self)
		if resolvers is None:
			resolvers = {}
		if "raw" not in resolvers:
			resolvers["raw"] = ContentAPIResolver(self, "api/v1/article/raw/")
		if "text" not in resolvers:
			resolvers["text"] = ContentAPIResolver(self, "api/v1/article/text/")
		self.resolvers = resolvers
		self.cache = cache

	def _perform_request(self, method, endpoint, data, params, json=True):
		resp = method(
			self.host + endpoint,
			data = data,
			params = params,
			auth = self._auth,
		)
		if json:
			return JSONResponse(resp)
		else:
			return RawResponse(resp)

	def perform_get(self, endpoint, data=None, params=None, json=True):
		try_cache = (json == True) and (self.cache is not None)
		if try_cache:
			resp = self.cache.get(endpoint, data, params)
			if resp:
				return resp
		resp = self._perform_request(requests.get, endpoint, data, params, json)
		if try_cache and resp.ok:
			self.cache.set(endpoint, data, params, resp)
		return resp

	def perform_post(self, endpoint, data=None, params=None, json=True):
		return self._perform_request(requests.post, endpoint, data, params, json)

	def get_raw(self, articlecontent):
		return self.resolvers["raw"].get(articlecontent)

	def get_text(self, articlecontent):
		return self.resolvers["text"].get(articlecontent)
