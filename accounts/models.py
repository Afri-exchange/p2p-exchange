from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
# Create your models here.


class Accounts(models.Model):
    acc_balance = models.DecimalField(max_digits=19, decimal_places=8, validators=[
        MinValueValidator(Decimal('0.00000000'), message="Ensure this value is greater than or equal to 0.")])
    owned_by = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='account')
