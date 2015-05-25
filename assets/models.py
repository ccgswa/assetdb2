import datetime
from django.db import models
from django.contrib.auth.models import User

# TODO Confirm Asset model specification.

# Abstract class inherited by all models. NO LONGER NEEDED AFTER IMPLEMENTING REVERSION
#class AbstractClass(models.Model):
#    created_by = models.ForeignKey(User, editable=False)
#    created_date = models.DateTimeField(auto_now_add = True)
#    edited_by = models.ForeignKey(User)
#    edited_date = models.DateTimeField(auto_now_add = True)
#    class Meta:
#        abstract = True


class Asset(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    model = models.CharField(max_length=200, blank=True, null=True)
    serial = models.CharField('Serial Number', max_length=200, unique=True)

    LOCATION_CHOICES = (
        ('none', 'None'),
        ('ccgs', 'CCGS: Main Campus'),
        ('kooringal', 'Kooringal Campus'),
        ('damaged', 'Damaged'),
        ('disposed', 'Disposed'),
        ('lost', 'Lost or Stolen')
    )
    # Merge with location (legacy) on import
    location = models.CharField(max_length=200, choices=LOCATION_CHOICES, default='none')
    owner = models.CharField(max_length=200, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
#   invoice_numbers = Is this required? May need to update function requirements. Ask Geoff.
    wired_mac = models.CharField('Wired MAC', max_length=200, unique=True, blank=True, null=True)
    wireless_mac = models.CharField('Wireless MAC', max_length=200, unique=True, blank=True, null=True)
    bluetooth_mac = models.CharField('Bluetooth MAC', max_length=200, unique=True, blank=True, null=True)
    far_asset = models.BooleanField('FAR Asset', default=False)
    far_cost = models.CharField(max_length=200, blank=True, null=True)
    ed_cost = models.CharField('Educational Cost', max_length=200, blank=True, null=True)
    warranty_period = models.CharField(max_length=200, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset)

    INCIDENT_CHOICES = (
        ('general', 'General Note'),
        ('deploy', 'Deploy to Staff/Student'),
        ('return', 'Return to ICT'),
        ('lost', 'Lost or Stolen'),
        ('decommission', 'Decommission'),
        ('dispose', 'Dispose'),
    )
    incident = models.CharField(max_length=200, choices=INCIDENT_CHOICES, default='general')

    recipient = models.CharField(max_length=200, blank=True, null=True)

    TRANSFER_CHOICES = (
        ('internal', 'Internal'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    )
    transfer = models.CharField(max_length=200, choices=TRANSFER_CHOICES, default='internal')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.notes