# import requests
# from django.http import HttpResponseRedirect
#
# from isc_common.http.DSRequest import DSRequest
# from django.conf import settings
#
#
# def uploadKompasFile(request):
#     _request = DSRequest(request=request)
#     data = _request.get_data()
#
#     id = data.get('id')
#     userId = data.get('userId')
#     wsHost = data.get('wsHost')
#     wsPort = data.get('wsPort')
#     wsChannel = data.get('wsChannel')
#
#     r = requests.get(f'{settings.KOMPAS_INFORMICA}/logic/Documents/UploadKompas', params=dict(id=id, wsPort=wsPort, wsHost=wsHost, wsChannel=wsChannel, userId=userId))
#     return HttpResponseRedirect(r.url)
#
#
# def uploadPdfFile(request):
#     return HttpResponseRedirect(f'{settings.KOMPAS_INFORMICA}/logic/Documents/UploadPdf/')
