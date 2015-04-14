import datetime
from django.db import models

# Create your models here.

class Asset(models.Model):
    name = models.CharField(max_length=30, primary_key=True, unique=True)
    manufacturer = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)
    serial = models.CharField(max_length=50, unique=True)

    LOCATION_CHOICES = (
        ('none', 'None'),
        ('ccgs', 'CCGS: Main Campus'),
        ('koor', 'Kooringal Campus'),
        ('dmg', 'Damaged'),
        ('disp', 'Disposed'),
        ('lost', 'Lost or Stolen')
    )
    location = models.CharField(max_length=4, choices=LOCATION_CHOICES, default='none' )

    owner = models.CharField(null=True, max_length=50)
    purchase_date = models.DateField(null=True)
    created_date = models.DateField(null=True)
    mac = models.CharField(max_length=50, unique=True, null=True)
    wmac = models.CharField(max_length=50, unique=True, null=True)
    bmac = models.CharField(max_length=50, unique=True, null=True)
    active = models.BooleanField(default=True)

