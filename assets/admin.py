from django.contrib import admin
from models import Asset

class AssetAdmin(admin.ModelAdmin):
    """
    AssetAdmin
    """

    list_display = ('name', 'serial', 'owner', 'active', 'purchase_date')
    search_fields = ['name', 'serial']



# Register your models here.

admin.site.register(Asset, AssetAdmin)