from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Payment_method(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=100)
    cardholder_name = models.CharField(max_length=100)
    expiration_month = models.IntegerField()
    expiration_year = models.IntegerField()



