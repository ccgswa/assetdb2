__author__ = 'gnolan'

from django import template
from assets import models
from assets.forms import AssetHistoryForm
from django.forms.models import inlineformset_factory

register = template.Library()


@register.inclusion_tag('admin/assets/asset_history.html')
def display_asset_history(asset_id):
    asset = models.Asset.objects.get(id__exact=asset_id)
    asset_history = models.AssetHistory.objects.filter(asset=asset)
    return {'asset_history': asset_history}




# TODO Find out how to render an inline form for editing Asset History using the following broken code. See https://docs.djangoproject.com/en/1.8/topics/forms/formsets/
#@register.inclusion_tag('admin/assets/asset_history.html')
#def asset_history_form(asset_id):
#    AssetHistoryFormSet = inlineformset_factory(Asset, AssetHistory, fields=('incident', 'recipient', 'transfer', 'notes',))
#    asset = models.Asset.objects.get(id__exact=asset_id)
#    formset = AssetHistoryFormSet(instance=asset)
#    return {'formset': formset}

