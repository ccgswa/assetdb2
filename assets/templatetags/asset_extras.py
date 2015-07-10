__author__ = 'gnolan'

from django import template
from assets import models

register = template.Library()


@register.inclusion_tag('admin/assets/asset_history.html')
def display_asset_history(asset_id):
    asset = models.Asset.objects.get(id__exact=asset_id)
    asset_history = models.AssetHistory.objects.filter(asset=asset).order_by('created_date')
    return {'asset_history': asset_history}


