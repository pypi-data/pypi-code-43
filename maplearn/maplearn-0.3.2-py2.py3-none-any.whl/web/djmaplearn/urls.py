from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from djmaplearn.views import JobCreate, JobList, JobDetail

urlpatterns = [
    url(r'jobs/add/$', JobCreate.as_view(), name='job-add'),
    url(r'jobs/$', JobList.as_view(), name='job-list'),
    url(r'jobs/(?P<pk>[-\d]+)/$', JobDetail.as_view(), name='job-detail'),
    # url(r'jobs/report/(?P<pk>[-\d]+)/$', JobReport.as_view(),
    #    name='job-report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
