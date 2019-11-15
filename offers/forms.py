from django import forms
from offers.models import Offers


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offers
        # fields = "__all__"
        fields = ['avail_amount', 'fiat_currency', 'pay_method',
                  'min_amount', 'max_amount', 'margin_percent']
