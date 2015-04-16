from django.contrib import admin
from models import Asset, AssetHistory

#TODO Explore further customisations https://docs.djangoproject.com/en/1.8/intro/tutorial02/#customizing-your-application-s-templates

class HistoryInline(admin.StackedInline):
    model = AssetHistory
    extra = 1

class AssetAdmin(admin.ModelAdmin):
    """
    AssetAdmin
    """

    list_display = ('name', 'serial', 'owner', 'active', 'purchase_date')
    search_fields = ['name', 'serial']
    inlines = [
        HistoryInline,
    ]

# Register your models here.

admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetHistory)