from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.core.urlresolvers import reverse_lazy

from djmaplearn.models import Job


class JobCreate(CreateView):
    model = Job
    fields = ['sample', 'klass_id', 'klass', 'features', 'codes', 'data',
              'scale', 'balance', 'reduction', 'ncomp', 'separability',
              'treatment_type', 'distance', 'algorythm', 'optimisation',
              'prediction']
    template_name = 'job_form.html'
    success_url = reverse_lazy('job-list')


class JobList(ListView):
    model = Job
    template_name = 'job_list.html'


class JobDetail(DetailView):
    model = Job
    template_name = 'job_detail.html'
