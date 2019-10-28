import ujson
import aiohttp
import hashlib


async def PostHttpJson(url, params={}, json={}, headers={}, **kwargs):
    """
    self,
    method: str,
    str_or_url: StrOrURL, *,
    params: Optional[Mapping[str, str]]=None,
    data: Any=None,
    json: Any=None,
    cookies: Optional[LooseCookies]=None,
    headers: LooseHeaders=None,
    skip_auto_headers: Optional[Iterable[str]]=None,
    auth: Optional[BasicAuth]=None,
    allow_redirects: bool=True,
    max_redirects: int=10,
    compress: Optional[str]=None,
    chunked: Optional[bool]=None,
    expect100: bool=False,
    raise_for_status: Optional[bool]=None,
    read_until_eof: bool=True,
    proxy: Optional[StrOrURL]=None,
    proxy_auth: Optional[BasicAuth]=None,
    timeout: Union[ClientTimeout, object]=sentinel,
    verify_ssl: Optional[bool]=None,
    fingerprint: Optional[bytes]=None,
    ssl_context: Optional[SSLContext]=None,
    ssl: Optional[Union[SSLContext, bool, Fingerprint]]=None,
    proxy_headers: Optional[LooseHeaders]=None,
    trace_request_ctx: Optional[SimpleNamespace]=None
    """
    if "content-type" not in headers:
        headers["content-type"] = "application/json"
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(url,
                                params=params,
                                json=json,
                                headers=headers,
                                **kwargs) as resp:
            return await resp.json(content_type=None)


async def GetHttpJson(url, params={}, json={}, headers={}, **kwargs):
    """
    self,
    method: str,
    str_or_url: StrOrURL, *,
    params: Optional[Mapping[str, str]]=None,
    data: Any=None,
    json: Any=None,
    cookies: Optional[LooseCookies]=None,
    headers: LooseHeaders=None,
    skip_auto_headers: Optional[Iterable[str]]=None,
    auth: Optional[BasicAuth]=None,
    allow_redirects: bool=True,
    max_redirects: int=10,
    compress: Optional[str]=None,
    chunked: Optional[bool]=None,
    expect100: bool=False,
    raise_for_status: Optional[bool]=None,
    read_until_eof: bool=True,
    proxy: Optional[StrOrURL]=None,
    proxy_auth: Optional[BasicAuth]=None,
    timeout: Union[ClientTimeout, object]=sentinel,
    verify_ssl: Optional[bool]=None,
    fingerprint: Optional[bytes]=None,
    ssl_context: Optional[SSLContext]=None,
    ssl: Optional[Union[SSLContext, bool, Fingerprint]]=None,
    proxy_headers: Optional[LooseHeaders]=None,
    trace_request_ctx: Optional[SimpleNamespace]=None
    """
    if "content-type" not in headers:
        headers["content-type"] = "application/json"
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.get(url,
                               params=params,
                               json=params,
                               headers=headers,
                               **kwargs) as resp:
            return await resp.json(content_type=None)


def GetMD5(encryption):
    """
    对字符串进行md5加密
    """
    m = hashlib.md5()
    b = encryption.encode(encoding='utf-8')
    m.update(b)
    return m.hexdigest()


def isNoneOrEmpty(obj):
    '''
    判断列表或者字符串是否为空
    '''
    if obj is None:
        return True
    if isinstance(obj, list):
        return len(obj) <= 0
    if isinstance(obj, str):
        return len(obj.replace(' ', '')) <= 0
    return True