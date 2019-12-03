from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _
from django import forms
# Create your models here.


class Offers(models.Model):
    CURRENCY = (
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    )
    METHOD_PAY = (
        ('Amazon Gift Card', 'Amazon Gift Card'),
        ('Paypal', 'PayPal'),
        ('Walmart Gift Card', 'Walmart Gift Card'),)
    fiat_currency = models.CharField(
        max_length=3, choices=CURRENCY, default=CURRENCY[0][0])
    pay_method = models.CharField(
        max_length=50, choices=METHOD_PAY, default=METHOD_PAY[0][0])
    min_amount = models.PositiveIntegerField()
    max_amount = models.PositiveIntegerField()
    margin_percent = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)])
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='offers')

    class Meta:
        db_table = "offers"


class Bids(models.Model):
    STATES = (
        ('OPEN', 'OPEN'),
        ('ACCEPTED', 'ACCEPTED'),
        ('DECLINED', 'DECLINED'),
    )
    amount = models.PositiveIntegerField()
    offer = models.ForeignKey(
        Offers, on_delete=models.CASCADE, related_name='bids')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bids')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=8, choices=STATES, default=STATES[0][0])

    class Meta:
        db_table = "bids"

    # def clean(self):
    #     self.offer = 
    #     if self.amount > self.offer.max_amount:
    #         raise ValidationError(
    #             {'amount': _("Bid can't be greater than {}".format(self.offer.max_amount))})
    #     if self.amount < self.offer.min_amount:
    #         raise ValidationError(
    #             {'amount': _("Bid can't be less than {}".format(self.offer.min_amount))})

    def validate_amount(self):
        if self.amount > self.offer.max_amount:
            raise ValidationError([
                {NON_FIELD_ERRORS: _("Bid can't be greater than {}".format(self.offer.max_amount))}])
        if self.amount < self.offer.min_amount:
            raise ValidationError([
                {NON_FIELD_ERRORS: _("Bid can't be less than {}".format(self.offer.min_amount))}])

