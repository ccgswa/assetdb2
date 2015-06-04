from django import forms
# from django.forms import ModelForm
from assets.models import AssetHistory


class AssetDecommissionForm(forms.Form):
    location = forms.CharField(label='Location', max_length=100)
    owner = forms.CharField(label='Owner', max_length=100)
    active = forms.BooleanField(label='Active')
    indicent = forms.CharField(label='Incident', max_length=100)
    recipient = forms.CharField(label='Recipient', max_length=100)
    transfer = forms.CharField(label='Transfer', max_length=100)
    notes = forms.CharField(label='Notes', max_length=100)


class AssetHistoryForm(forms.ModelForm):
    class Meta:
        model = AssetHistory
        fields = ['incident', 'recipient', 'transfer', 'notes']

