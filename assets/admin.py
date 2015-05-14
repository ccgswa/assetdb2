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
    readonly_fields = ['created_date', 'created_by']
    search_fields = ['name', 'serial','wmac']
    inlines = [
        HistoryInline,
    ]
    # Custom save to allow setting of uneditable created_by field
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

# Register your models here.

admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetHistory)