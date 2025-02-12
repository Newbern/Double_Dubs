from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Payment_method(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=100, null=True, blank=False)
    card_id = models.CharField(max_length=100, null=True, blank=False)
    last_4 = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"{self.username}: {self.last_4}"


class Order(models.Model):
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
    completed_status = models.BooleanField(default=False, null=False)
    refund_status = models.BooleanField(default=False, null=False)
    order_id = models.IntegerField(null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=False, blank=False)
    payment_id = models.CharField(max_length=100, null=False, blank=False)
    card_last_4 = models.CharField(max_length=4, null=True, blank=True)
    total_payment = models.DecimalField(max_digits=10000, decimal_places=2, null=True, blank=True)
    cart = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.username}: {self.order_id}"
