#!/usr/bin/env python
# coding: utf-8
'''Sites information de Iydon.
'''
__all__ = ('get_all_links', 'get_link_by_subdomain')
def __dir__() -> list: return __all__


from .config import domain, subdomains
from .utils import typeassert, domain_join


@typeassert(str, bool, bool)
def get_link_by_subdomain(subdomain, parse=False, full=False) -> str:
	'''Get link by subdomain.

	Argument
	=======
		subdomain: str
		parse: bool, whether to parse
		full: bool, whether to return full link

	Return
	=======
		str, full link
	'''
	assert subdomain in subdomains, '`{}` not in subdomains.'.format(subdomain)
	url = (subdomains[subdomain].link, ) if parse else (subdomain, domain)
	return domain_join(url, full, subdomains[subdomain].https)


@typeassert(bool, bool)
def get_all_links(parse=False, full=False) -> list:
	'''Get all links de Iydon.

	Argument
	=======
		parse: bool, whether to parse
		full: bool, whether to return full link

	Return
	=======
		list with all str, full links
	'''
	return [get_link_by_subdomain(subdomain, parse, full) \
		for subdomain in subdomains]
