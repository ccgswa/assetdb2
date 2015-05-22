from django.contrib import admin
from models import Asset, AssetHistory
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import reversion

#TODO Explore further customisations https://docs.djangoproject.com/en/1.8/intro/tutorial02/#customizing-your-application-s-templates

# Inline for displaying asset history on Asset admin page
class HistoryInline(admin.StackedInline):
    model = AssetHistory
    extra = 1
    verbose_name = 'Asset History'
    verbose_name_plural = 'Asset History'
    can_delete = False
    template = 'admin/assets/assethistory/edit_inline/stacked.html'

# For importing and exporting Asset data
class AssetResource(resources.ModelResource):

    class Meta:
        model = Asset



#TODO Override default template to enable import/export buttons etc.

class AssetAdmin(reversion.VersionAdmin, ImportExportModelAdmin):
    """
    AssetAdmin
    """
#   For custom change_form template name
#   change_form_template = 'admin/assets/asset/change_form.html'

    list_display = ('name', 'serial', 'owner', 'active', 'purchase_date')
#    readonly_fields = ['created_date', 'created_by'] #DEPRECATED. USING REVERSION
    search_fields = ['name', 'serial', 'wireless_mac']
    inlines = [
        HistoryInline,
    ]

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetResource
    pass


# For importing and exporting Asset History data
class AssetHistoryResource(resources.ModelResource):

    class Meta:
        model = AssetHistory


class AssetHistoryAdmin(reversion.VersionAdmin, ImportExportModelAdmin):
    """
    AssetHistoryAdmin
    """

    list_display = ('asset', 'incident', 'notes')
    search_fields = ['asset', 'notes']

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetHistoryResource
    pass

    # Custom save to allow setting of read only created_by field. NO LONGER NEEDED AFTER IMPLEMENTING REVERSION
#    def save_model(self, request, obj, form, change):
#        obj.created_by = request.user
#        obj.save()


admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetHistory, AssetHistoryAdmin)