from django import forms
from django.forms import ModelForm
from assets.models import Asset
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
    location = forms.ChoiceField(label='Select an incident', widget=forms.RadioSelect, choices=location_choices, initial='damaged')
    recipient = forms.CharField(label='New location or recipient', max_length=200,
                                widget=forms.TextInput(attrs={'size': 40}),
                                help_text="Examples: \'Repair\', \'Disposed\', \'Lost\', \'Geoff\'s house\'.")
    notes = forms.CharField(label='Additional Notes', widget=forms.Textarea(attrs={'rows': 2, 'cols': 60}),
                            help_text="Example: \'Processed for repair with Winthrop (cracked screen)\'.")


class AssetCSVUploadForm(forms.Form):
    csvfile = forms.FileField(label='CSV File')

class AssetDeploymentForm(forms.Form):
    deploy_choices = (
        ('deploy_student', 'Student'), ('deploy_staff', 'Staff Member'),
    )
    deploy_to = forms.ChoiceField(label='Deploy to', widget=forms.RadioSelect, choices=deploy_choices, initial='deploy_student')
    recipient = forms.CharField(label='Recipient', widget=forms.TextInput(attrs={'size': 40}),
                                help_text="You must include the student ID when deploying to a student.<br> "
                                          "Format: \'Jimmy Jones - 11111\'")
    location_choices = (
        ('ccgs', 'CCGS Main Campus'), ('kooringal', 'Kooringal Campus'), ('none', '--------------------'),
    )
    location = forms.ChoiceField(label='Location', choices=location_choices, initial='ccgs')
    replacing = forms.CharField(label='Replacement for (optional)', max_length=200, required=False,
                                help_text="Enter the previous asset owned by this recipient <br> Example: \'ITE1234\'")


class AssetReactivationForm(forms.Form):
    reason = forms.CharField(label='Reason', widget=forms.Textarea(attrs={'rows': 2, 'cols': 60}),
                             help_text="Example: Rejected by repairer. Still functional. "
                                       "Asset returned to ICT for re-purposing.")


class AssetCSVDeploymentForm(forms.Form):
    deploy_choices = (
        ('deploy_student', 'Student'), ('deploy_staff', 'Staff Member'),
    )
    deploy_to = forms.ChoiceField(label='Deploy to', widget=forms.RadioSelect, choices=deploy_choices, initial='deploy_student')
    location_choices = (
        ('ccgs', 'CCGS Main Campus'), ('kooringal', 'Kooringal Campus'), ('none', '--------------------'),
    )
    location = forms.ChoiceField(label='Location', choices=location_choices, initial='ccgs')
    csvfile = forms.FileField(label='CSV File')

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