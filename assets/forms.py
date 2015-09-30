from django import forms
from django.forms import ModelForm
from assets.models import Asset, AssetHistory
from validators import clean_mac


class AssetAdminForm(forms.ModelForm):

    class Meta:
        model = Asset
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(),

        }

    def clean_wired_mac(self):
        value = self.cleaned_data['wired_mac']
        return clean_mac(value)

    def clean_wireless_mac(self):
        value = self.cleaned_data['wireless_mac']
        return clean_mac(value)

    def clean_bluetooth_mac(self):
        value = self.cleaned_data['bluetooth_mac']
        return clean_mac(value)


class AssetDecommissionForm(forms.Form):
    location_choices = (
        ('damaged', 'Damaged'), ('lost', 'Lost or Stolen'), ('disposed', 'Disposed'),
    )
    location = forms.ChoiceField(label='Incident', widget=forms.RadioSelect, choices=location_choices, initial='damaged')
    recipient = forms.CharField(label='Recipient', max_length=200)
    notes = forms.CharField(label='Notes', widget=forms.Textarea)


class AssetDeploymentForm(forms.Form):
    deploy_choices = (
        ('deploy_student', 'Student'), ('deploy_staff', 'Staff Member'),
    )
    deploy_to = forms.ChoiceField(label='Deploy to', widget=forms.RadioSelect, choices=deploy_choices, initial='deploy_student')
    recipient = forms.CharField(label='Recipient')
    location_choices = (
        ('ccgs', 'CCGS Main Campus'), ('kooringal', 'Kooringal Campus'), ('none', '--------------------'),
    )
    location = forms.ChoiceField(label='Location', choices=location_choices, initial='ccgs')
    exact_location = forms.CharField(label='Year/Dept/Room', max_length=200, required=False)
    replacing = forms.CharField(label='Replacement for', max_length=200, required=False)


class iPadReplacementForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['name',
                  'manufacturer',
                  'model',
                  'serial',
                  'wireless_mac',
                  'bluetooth_mac',
                  'purchase_date',
                  'ed_cost',
                  'far_cost',
                  'warranty_period',
                  'active']