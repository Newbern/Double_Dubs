from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.


class Account(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    employee = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=10, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    zip = models.IntegerField(null=True, blank=True)
    cart = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.username}'


class Sauce(models.Model):
    name = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='sauces/', null=True, blank=True, default='default/no_image.png')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    instock = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Making sure there is a Image
        if self.image:
            if self.image != 'default/no_image.png':
                # Making sure Image path exist
                if os.path.isfile(self.image.path):
                    # Deleting File
                    os.remove(self.image.path)

        # Deletes Content
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        print(self.image)

        # Self.pk is the New Data
        if self.pk:
            # Getting Old Data back
            old_pk = Sauce.objects.get(pk=self.pk)
            old_image = old_pk.image

            # Checking if Image is being updated
            if self.image != old_image:
                # Making sure file still exist
                if old_image and os.path.isfile(old_image.path):
                    # Deleting Old image
                    os.remove(old_image.path)

        # Saving New Image
        super(Sauce, self).save(*args, **kwargs)
