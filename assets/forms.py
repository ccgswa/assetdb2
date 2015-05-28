from django.forms import ModelForm
from assets.models import AssetHistory


class AssetHistoryForm(ModelForm):
    class Meta:
        model = AssetHistory
        fields = ['incident', 'recipient', 'transfer', 'notes']

