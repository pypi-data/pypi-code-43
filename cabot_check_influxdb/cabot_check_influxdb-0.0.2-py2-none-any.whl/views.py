from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from cabot.cabotapp.models import StatusCheck
from cabot.cabotapp.views import (CheckCreateView, CheckUpdateView,
                                  StatusCheckForm, base_widgets)

from .models import InfluxdbStatusCheck


class InfluxdbStatusCheckForm(StatusCheckForm):
    symmetrical_fields = ('service_set', 'instance_set')

    class Meta:
        model = InfluxdbStatusCheck
        fields = (
            'name',
            'host',
            'port',
            'timeout',
            'frequency',
            'active',
            'importance',
            'debounce',
        )

        widgets = dict(**base_widgets)
        widgets.update({
            'host': forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': 'service.arachnys.com',
            })
        })


class InfluxdbCheckCreateView(CheckCreateView):
    model = InfluxdbStatusCheck
    form_class = InfluxdbStatusCheckForm


class InfluxdbCheckUpdateView(CheckUpdateView):
    model = InfluxdbStatusCheck
    form_class = InfluxdbStatusCheckForm


def duplicate_check(request, pk):
    pc = StatusCheck.objects.get(pk=pk)
    npk = pc.duplicate()
    return HttpResponseRedirect(reverse('update-influxdb-check', kwargs={'pk': npk}))
