from ge_sm.common.secrets import *


chaajaauserpagesdimdict = {
	'ga_user_pages_C': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'Page Path': 'pagePath', 'Page Title': 'pageTitle'},
	'ga_user_pages_CK': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'KadenceId': 'dimension2', 'Page Path': 'pagePath', 'Page Title': 'pageTitle'},
	'ga_user_pages_CW': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'WagtailId': 'dimension3', 'Page Path': 'pagePath', 'Page Title': 'pageTitle'},
	'ga_user_pages_CKW': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'KadenceId': 'dimension2', 'WagtailId': 'dimension3', 'Page Path': 'pagePath', 'Page Title': 'pageTitle'}
}

chaajaausereventsdimdict = {
	'ga_user_events_C': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'Event Category': 'eventCategory', 'Event Label': 'eventLabel'},
	'ga_user_events_CK': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'KadenceId': 'dimension2', 'Event Category': 'eventCategory', 'Event Label': 'eventLabel'},
	'ga_user_events_CW': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'WagtailId': 'dimension3', 'Event Category': 'eventCategory', 'Event Label': 'eventLabel'},
	'ga_user_events_CKW': {'DateTime': 'dateHourMinute', 'ClientId': 'dimension1', 'KadenceId': 'dimension2', 'WagtailId': 'dimension3', 'Event Category': 'eventCategory', 'Event Label': 'eventLabel'}
}


chaajaauser = {
	'view': os.environ.setdefault('CHAAJAAUSER_VIEW', '****'),
	'viewId': os.environ.setdefault('CHAAJAAUSER_VIEWID', '****'),
	'pages': {
		'dimdict': chaajaauserpagesdimdict,
		'mets': {'Time on page': 'timeonpage', 'Page views': 'pageviews'}},
	'events': {
		'dimdict': chaajaausereventsdimdict,
		'mets': {'Total Events': 'totalevents', 'Unique Events': 'uniqueevents'}}
}



