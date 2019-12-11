from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class Accounts(models.Model):
    acc_balance = models.DecimalField(max_digits=36, decimal_places=18, validators=[
        MinValueValidator(Decimal('0.0000000'), message="Ensure this value is greater than or equal to 0.")])
    escrow_balance = models.DecimalField(max_digits=36, decimal_places=18, validators=[
        MinValueValidator(Decimal('0.0000000'), message="Ensure this value is greater than or equal to 0.")])
    owned_by = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='account')


class Profile(models.Model):
    BANKS = (
        ('Access Bank', 'Access Bank'),
        ('Fidelity Bank', 'Fidelity Bank'),
        ('FCMB', 'FCMB'),
        ('First Bank', 'First Bank'),
        ('GTB', 'GTB'),
        ('Union Bank', 'Union Bank'),
        ('UBA', 'UBA'),
        ('Zenith Bank', 'Zenith Bank'),
        ('CitiBank', 'CitiBank'),
        ('EcoBank', 'EcoBank'),
        ('Heritage Bank', 'Heritage Bank'),
        ('Keystone Bank', 'Keystone Bank'),
        ('Polaris Bank', 'Polaris Bank'),
        ('Stanbic IBTC', 'Stanbic IBTC'),
        ('Standard Chartered Bank', 'Standard Chartered Bank'),
        ('Sterling Bank', 'Sterling Bank'),
        ('Unity Bank', 'Unity Bank'),
        ('Wema Bank', 'Wema Bank'),)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bank_name = models.CharField(
        max_length=50, choices=BANKS, default=BANKS[0][0])
    account_number = models.CharField(
        validators=[MinLengthValidator(10), MaxLengthValidator(10)], max_length=10, unique=True)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
