from django import forms
from assets.models import Asset


class AssetAdminForm(forms.ModelForm):

    class Meta:
        model = Asset
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(),

        }


class AssetDecommissionForm(forms.Form):
    location_choices = (
        ('damaged', 'Damaged'), ('lost', 'Lost or Stolen'), ('disposed', 'Disposed'),
    )
    location = forms.ChoiceField(label='Incident', widget=forms.RadioSelect, choices=location_choices, initial='damaged')
    recipient = forms.CharField(label='Recipient', max_length=100)
    notes = forms.CharField(label='Notes', max_length=100)


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
    exact_location = forms.CharField(label='Year/Dept/Room', max_length=100, required=False)
    replacing = forms.CharField(label='Replacement for', max_length=100, required=False)