import datetime
from django.db import models
from django.contrib.auth.models import User

# Abstract class to track model changes
# class AbstractClass(models.Model):
#    created_by = models.ForeignKey(User, editable=False)
#    created_date = models.DateTimeField(auto_now_add=True)

#    class Meta:
#       abstract = True

# TODO https://docs.djangoproject.com/en/1.8/ref/validators/ to add validators to prevent entering commas

class Asset(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    serial = models.CharField('Serial Number', max_length=200, db_index=True, blank=True)

    LOCATION_CHOICES = (
        ('none', '--------------------'),
        ('ccgs', 'CCGS Main Campus'),
        ('kooringal', 'Kooringal Campus'),
        ('damaged', 'Damaged'),
        ('disposed', 'Disposed'),
        ('lost', 'Lost or Stolen')
    )
    # Merge with location (legacy) on import
    location = models.CharField(max_length=200, choices=LOCATION_CHOICES, default='none')
    exact_location = models.CharField('Year/Dept/Room', max_length=200, blank=True)
    owner = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    invoices = models.CharField('Invoice Numbers', max_length=200, blank=True)
    wired_mac = models.CharField('Wired MAC', max_length=200, blank=True)
    wireless_mac = models.CharField('Wireless MAC', max_length=200, blank=True)
    bluetooth_mac = models.CharField('Bluetooth MAC', max_length=200, blank=True)
    far_asset = models.BooleanField('FAR Asset', default=False)
    far_cost = models.CharField(max_length=200, blank=True)
    ed_cost = models.CharField('Educational Cost', max_length=200, blank=True)
    warranty_period = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name.encode('ascii', errors='replace')


class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name="history_created")
    created_date = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, editable=False, null=True, related_name="history_edited")
    edited_date = models.DateTimeField(auto_now=True, null=True)

    INCIDENT_CHOICES = (
        ('general', 'General Note'),
        ('deploy_staff', 'Deploy to Staff'),
        ('deploy_student', 'Deploy to Student'),
        ('return', 'Return to ICT'),
        ('lost', 'Lost or Stolen'),
        ('decommission', 'Decommission'),
        ('disposed', 'Disposed'),
    )
    incident = models.CharField(max_length=200, choices=INCIDENT_CHOICES, default='general')

    recipient = models.CharField(max_length=200, blank=True)

    TRANSFER_CHOICES = (
        ('internal', 'Internal'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    )
    transfer = models.CharField(max_length=200, choices=TRANSFER_CHOICES, default='internal')
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.notes.encode('ascii', errors='replace')

