from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.edit import FormView

from . import forms, services


class ContactRequestView(FormView):
    form_class = forms.ContactRequestForm
    template_name = 'djtools/contact/contactrequest_form.html'
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        """
        Displays a success message when the form is submitted correctly
        """

        services.create_contact_request(**form.cleaned_data)
        messages.success(self.request, _("Your request has been submitted."))
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Displays an error message when the form is submitted with errors
        """

        messages.error(self.request, _("Please, check the form errors."))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Adds extra information to the context data to be used in the template
        """

        context = super().get_context_data(**kwargs)
        context.update({
            'contact_information': services.get_contact_information(),
            'GMAPS_APIKEY': settings.DJTOOLS_CONTACT_GMAPS_APIKEY,
        })
        return context
