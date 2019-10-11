from django import forms


class PaymentForm(forms.Form):
    """
    PAYCOMET form with JETID will return amount and paytpvToken.
    paytpvToken field does not follow PEP8, but we will rename it in the view.
    """

    amount = forms.DecimalField()
    paytpvToken = forms.CharField(max_length=64)
