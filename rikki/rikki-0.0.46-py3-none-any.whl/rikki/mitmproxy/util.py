from mitmproxy import http
from rikki.mitmproxy.model import Request, Response
from typing import List, Optional, Dict
from mitmproxy.coretypes import multidict
from mitmproxy.net.http import Headers
from deepdiff import DeepDiff
import json
import re


def is_json(content: str):
    result = None
    try:
        result = json.loads(content)
    except ValueError:
        pass
    return result


def is_html(content: str):
    if content.lower().startswith("<!DOCTYPE html>".lower()):
        return True
    else:
        return False


def content_type(content: str) -> str:
    if is_json(content):
        return "application/json; charset=UTF-8"
    elif is_html(content):
        return "text/html; charset=utf-8"
    else:
        return "text/plain"


def replace(flow: http.HTTPFlow, request: Optional[Request] = None, response: Optional[Response] = None):
    if request:
        if request.host:
            flow.request.host = request.host
        if request.content:
            flow.request.content = request.content.encode("utf8")
        if request.params:
            for item in request.params.items():
                flow.request.query.set_all(item[0], [item[1]])
        if request.headers:
            for item in request.headers.items():
                headers: Headers = flow.request.headers
                headers.set_all(item[0], [item[1]])
    if response:
        if response.headers:
            for item in response.headers.items():
                headers: Headers = flow.response.headers
                headers.set_all(item[0], [item[1]])
        if response.content:
            flow.response.content = response.content.encode("utf8")
            flow.response.headers["Content-Type"] = content_type(response.content)
        if response.code:
            flow.response.status_code = response.code


def filter(
        flows: List[http.HTTPFlow],
        request: Optional[Request] = None,
        response: Optional[Response] = None
) -> List[http.HTTPFlow]:
    """
    Filter flows and return only those that contain data from filter params
    :param flows: list of flows to be filtered
    :param request: request data to look for during filter
    :param response: response data to look for during filter
    :return: new list of filtered flows
    """
    result: List[http.HTTPFlow] = []
    result.extend(flows)

    for flow in result:
        if request:
            if request.port and request.port != flow.request.port:
                if flow in result:
                    result.remove(flow)
                    continue
            if request.path and request.path != flow.request.path.split("?")[0]:
                if flow in result:
                    result.remove(flow)
                    continue
            if request.method and request.method != flow.request.method:
                if flow in result:
                    result.remove(flow)
                    continue
            if request.host:
                host_pattern = re.compile(f"{request.host}")
                """
                Use `Host` header as fallback when proxy works as transparent proxy and has only ip addresses
                """
                request_host = flow.request.host
                header_host = ""
                host_header_name = 'Host'
                if host_header_name in flow.request.headers:
                    header_host = flow.request.headers[host_header_name]
                if not host_pattern.fullmatch(request_host) and not host_pattern.fullmatch(header_host):
                    if flow in result:
                        result.remove(flow)
            if request.params and not contains_params(flow.request.query, request.params):
                if flow in result:
                    result.remove(flow)
                    continue
            if request.headers and not contains_headers(flow.request.headers, request.headers):
                if flow in result:
                    result.remove(flow)
                    continue
            if request.content:
                try:
                    content_decode = flow.request.raw_content.decode("utf8")
                except:
                    result.remove(flow)
                    continue

                if not compare_content(request.content, content_decode):
                    if flow in result:
                        result.remove(flow)
                        continue
        if response:
            if response.code and response.code != flow.response.status_code:
                if flow in result:
                    result.remove(flow)
            if response.headers and not contains_headers(flow.response.headers, response.headers):
                if flow in result:
                    result.remove(flow)
            if response.content and flow.response.content:
                try:
                    content_decode = flow.response.content.decode("utf8")
                except:
                    result.remove(flow)
                    continue

                if response.content.lower().strip() != content_decode.lower().strip():
                    if flow in result:
                        result.remove(flow)

    return result


def contains_params(base: multidict.MultiDictView, candidate: Dict) -> bool:
    for key in candidate.keys():
        if key in base.keys() and candidate[key] in base.get_all(key):
            continue
        else:
            return False
    return True


def contains_headers(headers: Headers, candidate: Dict[str, str]) -> bool:
    for key in candidate.keys():
        if key in headers.keys() and candidate[key] in headers.get_all(key):
            continue
        else:
            return False
    return True


def compare_content(left, right) -> bool:
    """
    If the left and right are JSON, will check that all key and values from left are in right.
    If they are not JSON. will compare as lower cased strings.
    THE IMPLEMENTATION RIGHT NOW IS AWKWARD, BUT IT WORKS.
    TODO: it's better to revisit the implementation and simple allow users to find all key and values from left in right
    :param left:
    :param right:
    :return:
    """
    left_json = None
    right_json = None

    if isinstance(left, str) and isinstance(right, str):
        if left.startswith("?{") or left.startswith("?["):
            left_json = is_json(left[1:])
            right_json = is_json(right)
            if not left_json or not right_json:
                return left[1:].lower().strip() == right.lower().strip()
        else:
            return left.lower().strip() == right.lower().strip()
    else:
        left_json = left
        right_json = right

    if left_json and right_json:
        diff = DeepDiff(left_json, right_json, ignore_order=True)
        if not diff:
            return True
        else:
            """
            Check if any of item from left was removed. We don't care if something was added from left
            """
            added_items = []
            removed_items = []
            changed_items = []
            for item in diff.items():
                if str(item[0]).endswith("_removed"):
                    removed_items.append(item[1])
                elif str(item[0]).endswith("_added"):
                    added_items.append(item[1])
                elif str(item[0]).endswith("_changed"):
                    changed_items.append(item[1])
                else:
                    pass

            if changed_items:
                return False

            if removed_items:
                for removed_item in removed_items:
                    item_completely_removed = True
                    if added_items:
                        for added_item in added_items:
                            if "root['root" in str(removed_item):
                                break
                            if compare_content(removed_item, added_item):
                                item_completely_removed = False
                                break
                        if item_completely_removed:
                            return False  # return False
            return True
