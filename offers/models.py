from django.db import models

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
    fiat_currency = models.CharField(max_length=3, choices=CURRENCY)
    pay_method = models.CharField(max_length=50, choices=METHOD_PAY)
    min_amount = models.IntegerField()
    max_amount = models.IntegerField()
    margin_percent = models.IntegerField()
    avail_amount = models.FloatField()

    class Meta:
        db_table = "offers"
