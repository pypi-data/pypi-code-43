from django.conf import settings
from django.views.generic import FormView

from . import services
from .exceptions import PaymentError
from .forms import PaymentForm
from .payment import PayCometClient


class PaymentView(FormView):
    form_class = PaymentForm

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'PAYCOMET_JET_ID': settings.PAYCOMET_JET_ID,
            'card_months': services.get_card_months(),
            'card_years': services.get_card_years(),
            'amount': self.get_amount(),
        }

    def get_amount(self):
        """
        Override this function to return the amount to be paid
        """
        raise NotImplementedError

    def form_valid(self, form):
        try:
            PayCometClient().create_payment(
                request=self.request,
                amount=form.cleaned_data['amount'],
                pay_tpv_token=form.cleaned_data['paytpvToken'],
            )
        except PaymentError as e:
            form.add_error(field=None, error=str(e))
            return self.form_invalid(form)
        else:
            self.actions_on_payment_success()
        return super().form_valid(form)

    def actions_on_payment_success(self):
        """
        Override this function if you want to send a confirmation email, for example
        """
        pass
