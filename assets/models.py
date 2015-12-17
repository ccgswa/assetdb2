from django.db import models
from django.contrib.auth.models import User
import reversion
from django.utils import timezone
from validators import validate_mac

# Abstract class to track model changes
# class AbstractClass(models.Model):
#    created_by = models.ForeignKey(User, editable=False)
#    created_date = models.DateTimeField(auto_now_add=True)

#    class Meta:
#       abstract = True

"""
IMPORTANT notes on model changes:

Any model changes that result in a migration will result in previous saved reversion versions no longer being
compatible with the new model. Previous reversion data will have to be deleted for this model to prevent revert errors.
Run the following:
                    ./manage.py deleterevisions assets.ModelNameGoesHere

Then run the following:
                    ./manage.py createinitialrevisions assets.ModelNameGoesHere

Notes on importing data:

1. Set up columns to match the Asset fields below in order. Add an 'id' column as the first but leave values blank.
2. If using Excel on a Mac save as Windows CSV (OTHER CSVs WILL NOT WORK)
3. Make sure the date column values are in the following format YYYY-mm-dd
4. Import away!

"""

# TODO https://docs.djangoproject.com/en/1.8/ref/validators/ to add validators to prevent entering commas


class Asset(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, db_index=True, blank=True)
    serial = models.CharField('Serial Number', max_length=200, db_index=True, blank=True)

    LOCATION_CHOICES = (
        ('none', '--------------------'),
        ('ccgs', 'CCGS Main Campus'),
        ('kooringal', 'Kooringal Campus'),
        ('damaged', 'Damaged'),
        ('disposed', 'Disposed'),
        ('lost', 'Lost or Stolen')
    )
    location = models.CharField(max_length=200, choices=LOCATION_CHOICES, default='none')
    exact_location = models.CharField('Legacy location', db_index=True, max_length=200, blank=True, default='ICT Services')
    owner = models.CharField(max_length=200, db_index=True, blank=True, default='ICT Services')
    purchase_date = models.DateField(help_text="Please use the following format: <em>YYYY-MM-DD</em>.",
                                     default=timezone.now)
    wired_mac = models.CharField('MAC', db_index=True, max_length=200, blank=True, validators=[validate_mac])
    wireless_mac = models.CharField('WiFi MAC', db_index=True, max_length=200, blank=True, validators=[validate_mac])
    bluetooth_mac = models.CharField('Bluetooth MAC', db_index=True, max_length=200, blank=True,
                                     validators=[validate_mac])
    far_asset = models.BooleanField('FAR Asset', default=False)
    far_cost = models.CharField(max_length=200, blank=True)
    ed_cost = models.CharField('Educational Cost', max_length=200, blank=True)
    warranty_period = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    invoices = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name.encode('ascii', errors='replace')

# Manually registering in models.py and setting follow to blank excludes inlines from reversion for this model.
# This is done to prevent errors due to the hidden foreign key fields 'created_by' and 'edited_by' not being rewritten
# when reverting an Asset. AssetHistory is now effectively decoupled from Asset version control.
reversion.register(Asset, follow=())


class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset, editable=False)
    created_by = models.ForeignKey(User, editable=False, null=True, related_name="history_created")
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

