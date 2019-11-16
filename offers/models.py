from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
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
    margin_percent = models.PositiveSmallIntegerField()
    avail_amount = models.DecimalField(max_digits=19, decimal_places=8, validators=[
                                       MinValueValidator(Decimal('0.00000001'), message="Ensure this value is greater than or equal to 0.00000001.")])
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='offers')

    class Meta:
        db_table = "offers"
