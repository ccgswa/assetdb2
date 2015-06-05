from django.contrib import admin
from django.contrib import messages
from models import Asset, AssetHistory
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from .forms import AssetDecommissionForm
from django.shortcuts import render
import reversion

# TODO Explore further customisations https://docs.djangoproject.com/en/1.8/intro/tutorial02/#customizing-your-application-s-templates
# TODO Edit history inline using IBM tutorial http://www.ibm.com/developerworks/opensource/library/os-django-admin/index.html

# TODO Implement Django Admin Actions for decommission
# https://docs.djangoproject.com/en/1.8/ref/contrib/admin/actions/
# OPTIONAL: http://stackoverflow.com/questions/2805701/is-there-a-way-to-get-custom-django-admin-actions-to-appear-on-the-change-view

# TODO Impelement django-object-actions to display admin actions on change_form
# TODO Add "Edit" button to toggle 'readonly' attribute for certain fields in change_form.

# TODO Override default template to enable import/export buttons etc.

# Inline for displaying asset history on Asset admin page. OVERRIDDEN BY CUSTOM TEMPLATE TAG
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


class AssetAdmin(DjangoObjectActions, reversion.VersionAdmin, ImportExportModelAdmin):
    """
    AssetAdmin
    """
#   For custom change_form template name
#   change_form_template = 'admin/assets/asset/change_form.html'

    list_display = ('name', 'serial', 'owner', 'active', 'purchase_date')
#   readonly_fields = ['created_date', 'created_by'] # Don't appear on change_form page. DEPRECATED. USING REVERSION
    search_fields = ['name', 'serial', 'wireless_mac']
    #save_on_top = True
    actions = ['decommission']
    objectactions = ('decommission', )


    inlines = [
        HistoryInline,
    ]

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetResource

    # Django Admin action to decommission an asset.
    # The django-object-actions decorator makes it available in change_form template.
    @takes_instance_or_queryset
    def decommission(self, request, queryset):

        # Check that we've submitted the decommission form
        if 'decommission_asset' in request.POST:
            # Create form object with submitted data
            form = AssetDecommissionForm(request.POST)
            if form.is_valid():
                # Use validated data to decommission selected assets
                for asset in queryset:
                    asset.location = form.cleaned_data['location']
                    asset.owner = '%s - Damaged' % asset.owner
                    asset.active = False
                    ah = AssetHistory(asset=asset,
                                      created_by=request.user,
                                      incident='decommission',
                                      recipient=form.cleaned_data['recipient'],
                                      transfer='outgoing',
                                      notes=form.cleaned_data['notes'])
                    asset.save()
                    ah.save()
                # Create message to user based on how many assets were updated
                rows_updated = len(queryset)
                if rows_updated == 1:
                    message_bit = "%s was" % queryset[0].name
                else:
                    message_bit = "%s assets were" % rows_updated
                self.message_user(request, "%s successfully decommissioned." % message_bit, level=messages.SUCCESS)
                return
        # For requests other than POST
        else:
            # Create a new form
            form = AssetDecommissionForm()
        # Render the empty form on a new page passing selected objects and form object fields as dictionaries
        return render(request, 'admin/assets/decommission.html', {'objects': queryset, 'form': form})

    # Names for django action tools
    decommission.short_description = "Decommission selected assets"
    decommission.label = "Decommission"
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