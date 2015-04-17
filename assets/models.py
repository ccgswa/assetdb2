import datetime
from django.db import models

# Create your models here.

#TODO Complete Asset model specification.
class Asset(models.Model):
    name = models.CharField(max_length=30, primary_key=True, unique=True)
    manufacturer = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    serial = models.CharField(max_length=50, unique=True)

    LOCATION_CHOICES = (
        ('none', 'None'),
        ('ccgs', 'CCGS: Main Campus'),
        ('koor', 'Kooringal Campus'),
        ('dmg', 'Damaged'),
        ('disp', 'Disposed'),
        ('lost', 'Lost or Stolen')
    )
    location = models.CharField(max_length=4, choices=LOCATION_CHOICES, default='none')

    owner = models.CharField( max_length=50, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    created_date = models.DateField(blank=True, null=True)
    mac = models.CharField(max_length=50, unique=True, blank=True, null=True)
    wmac = models.CharField(max_length=50, unique=True, blank=True, null=True)
    bmac = models.CharField(max_length=50, unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset)

    INCIDENT_CHOICES = (
        ('gen', 'General Note'),
        ('depl', 'Deploy to Staff/Student'),
        ('ict', 'Return to ICT'),
        ('lost', 'Lost or Stolen'),
        ('dec', 'Decommission'),
        ('disp', 'Disposed'),
    )
    incident = models.CharField(max_length=4, choices=INCIDENT_CHOICES, default='gen')
    recipient = models.CharField(max_length=50, blank=True, null=True)

    TRANSFER_CHOICES = (
        ('int', 'Internal'),
        ('inc', 'Incoming'),
        ('out', 'Outgoing')
    )
    transfer = models.CharField(max_length=4, choices=TRANSFER_CHOICES, default='int')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.incident