from django.views.generic import TemplateView, DetailView, ListView, CreateView, FormView
from system.models import Links
from django.conf import settings


def check_mobile(request):
    if settings.FORCE_MOBILE and request.site.siteproperty.stand_mobile:
        return True
    if (request.user_agent.is_mobile and request.site.siteproperty.stand_mobile) or int(request.GET.get('m', 0)) == 1:
        return True
    return False


class QtTemplateView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        self.template_name = set_template(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


class QtDetailView(DetailView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = set_template(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


class QtListView(ListView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = set_template(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


class QtCreateView(CreateView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = set_template(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


class QtFormView(FormView):
    def dispatch(self, request, *args, **kwargs):
        self.template_name = set_template(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links'] = Links.objects.filter(site=self.request.site).all()
        return context


def set_template(request, template_name):
    pre_name = request.template
    try:
        if check_mobile(request):
            template_name = 'm/' + template_name
    except Exception as e:
        print('There are no template found. %s' % str(e))
        template_name = template_name
    if pre_name != 'empty':
        return pre_name + '/' + template_name
    return template_name
