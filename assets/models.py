from django.db import models

# Create your models here.

class Asset(models.Model):
    name = models.CharField(max_length=30, primary_key=True, unique=True)
    serial = models.CharField(max_length= 50, unique=True)
    owner = models.CharField(max_length=50)
    purchase_date = models.DateField
    created_date = models.DateTimeField
    mac = models.CharField(max_length=50, unique=True)
    wmac = models.CharField(max_length=50, unique=True)
    bmac = models.CharField(max_length=50, unique=True)
    active = models.BooleanField
