from django import forms
from assets.models import AssetHistory


class AssetDecommissionForm(forms.Form):
    location = forms.CharField(label='Location', max_length=100)
    recipient = forms.CharField(label='Recipient', max_length=100)
    notes = forms.CharField(label='Notes', max_length=100)


class AssetHistoryForm(forms.BaseModelForm):
    class Meta:
        model = AssetHistory
        fields = ['incident', 'recipient', 'transfer', 'notes']

