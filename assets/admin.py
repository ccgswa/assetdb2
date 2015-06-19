from django.db import models
from django import forms
from django.contrib import admin
from django.contrib import messages
from models import Asset, AssetHistory
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from .forms import AssetDecommissionForm,AssetDeploymentForm, AssetAdminForm
from django.shortcuts import render
import reversion

# TODO Explore further customisations https://docs.djangoproject.com/en/1.8/intro/tutorial02/#customizing-your-application-s-templates

# TODO Add "Edit" button to toggle 'readonly' attribute for certain fields in change_form.

# TODO Override default template to enable import/export buttons etc.

# TODO Add CSS and JQuery to admin classes using the Media inner class https://docs.djangoproject.com/en/dev/ref/contrib/admin/#modeladmin-asset-definitions


# Inline for displaying asset history on Asset admin page. OVERRIDDEN BY CUSTOM TEMPLATE TAG
class HistoryInline(admin.StackedInline):
    model = AssetHistory
    verbose_name = 'Asset History'
    verbose_name_plural = 'Asset History'
    can_delete = False
    template = 'admin/assets/assethistory/edit_inline/stacked.html'
    fields = (('incident', 'transfer'), 'recipient', 'notes')
    extra = 1

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
                           attrs={'rows': 1,
                                  'cols': 100,
                                  'style': 'height: 2em;'})},
    }

    def get_queryset(self, request):
        """Alter the queryset to return no existing entries (only the extra!!)"""
        # Get the existing queryset, then empty it.
        qs = super(HistoryInline, self).get_queryset(request)
        return qs.none()



# For importing and exporting Asset data
class AssetResource(resources.ModelResource):

    class Meta:
        model = Asset


class AssetAdmin(DjangoObjectActions, reversion.VersionAdmin, ImportExportModelAdmin):
    """
    AssetAdmin
    """
#   For custom change_form template (i.e. override title etc)
#   change_form_template = 'admin/assets/asset/change_form.html'
    change_list_template = 'admin/assets/asset/change_list.html'

    form = AssetAdminForm

    search_fields = ['name', 'serial', 'wireless_mac']
    list_display = ('name', 'serial', 'owner', 'active', 'purchase_date')
#   readonly_fields = ['created_date', 'created_by'] # Don't appear on change_form page. DEPRECATED. USING REVERSION
    fieldsets = (
        (None, {
            'fields': (('name', 'owner', 'active'),
                       ('serial', 'location', 'spec_location'),
                       ('manufacturer', 'model'),
                       ('wireless_mac', 'wired_mac', 'bluetooth_mac'))
        }),
        ('Financial', {
            'classes': ('collapse',),
            'fields': (('far_asset', 'far_cost', 'ed_cost'), ('purchase_date', 'warranty_period'))
        }),

    )

    # save_on_top = True
    actions = ['decommission', 'deploy']
    objectactions = ('decommission', 'deploy', )

    inlines = [
        HistoryInline,
    ]

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetResource

    # Django Admin action to decommission an asset.
    # The django-object-actions decorator makes it available in change_form template.
    @takes_instance_or_queryset
    def decommission(self, request, queryset):

        # The user cancelled. Return to the change list.
        if 'cancel' in request.POST:
            self.message_user(request, 'Decommission cancelled.', level=messages.ERROR)
            return

        # Check that we've submitted the decommission form
        elif 'decommission_asset' in request.POST:
            # Create form object with submitted data
            form = AssetDecommissionForm(request.POST)
            if form.is_valid():

                # Prepare message string variables
                rows_updated = len(queryset)
                already_active = 0
                error_bit = ""

                # Use validated data to decommission selected assets
                for asset in queryset:
                    if asset.active:
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
                    else:
                        already_active += 1
                        if already_active == 1:
                            error_bit += asset.name
                        else:
                            error_bit += ", %s" % asset.name

                rows_updated -= already_active

                # Pluralize error string
                if already_active == 1:
                    error_bit += " was already deactivated."
                elif already_active > 1:
                    error_bit += " were already deactivated."
                else:
                    error_bit = ""

                # Construct message to user based on how many assets were updated
                if rows_updated == 1:
                    message_bit = "%s was" % queryset[0].name
                else:
                    message_bit = "%s assets were" % rows_updated
                self.message_user(request, "%s successfully decommissioned. %s" % (message_bit, error_bit), level=messages.SUCCESS)
                return

        # We've submitted a different form (i.e. change list/form). Go to the decommission form.
        else:
            # Create a new decommission form
            form = AssetDecommissionForm()
        # Render the empty form on a new page passing selected assets and form object fields as dictionaries
        return render(request, 'admin/assets/decommission.html',
                      {'objects': queryset, 'form': form})

    # Names for django action tools
    decommission.short_description = "Decommission selected assets"
    decommission.label = "Decommission"

    # Django Admin action to decommission an asset.
    # The django-object-actions decorator makes it available in change_form template.
    @takes_instance_or_queryset
    def deploy(self, request, queryset):

        # The user cancelled. Return to the change list.
        if 'cancel' in request.POST:
            self.message_user(request, 'Deployment cancelled.', level=messages.ERROR)
            return

        # Check that we've submitted the decommission form
        elif 'deploy_asset' in request.POST:
            # Create form object with submitted data
            form = AssetDeploymentForm(request.POST)

            if form.is_valid():

                # Prepare message string variables
                rows_updated = len(queryset)
                deactivated = 0
                error_bit = ""

                # Use validated data to decommission selected assets
                for asset in queryset:

                    if not asset.active:
                        deactivated += 1
                        if deactivated == 1:
                            error_bit += asset.name
                        else:
                            error_bit += ", %s" % asset.name

                    asset.location = form.cleaned_data['location']
                    asset.owner = form.cleaned_data['recipient']
                    asset.active = True
                    ah = AssetHistory(asset=asset,
                                      created_by=request.user,
                                      incident=form.cleaned_data['deploy_to'],
                                      recipient=form.cleaned_data['recipient'],
                                      transfer='internal',
                                      notes='Deployed to %s as replacement for %s' % (form.cleaned_data['recipient'],
                                                                                      form.cleaned_data['replacing']))

                    asset.save()
                    ah.save()

                rows_updated -= deactivated

                # Pluralize error string
                if deactivated == 1:
                    error_bit += " was reactivated. Please double check asset history."
                elif deactivated > 1:
                    error_bit += " were reactivated. Please double check asset history."
                else:
                    error_bit = ""

                # Construct message to user based on how many assets were updated
                if rows_updated == 1:
                    message_bit = "%s was" % queryset[0].name
                else:
                    message_bit = "%s assets were" % rows_updated
                self.message_user(request, "%s successfully deployed. %s" % (message_bit, error_bit), level=messages.SUCCESS)
                return

        # We've submitted a different form (i.e. change list/form). Go to the decommission form.
        else:
            # Create a new decommission form
            form = AssetDeploymentForm()
        # Render the empty form on a new page passing selected assets and form object fields as dictionaries
        return render(request, 'admin/assets/deploy.html',
                      {'objects': queryset, 'form': form})


    deploy.short_description = "Deploy selected assets"
    deploy.label = "Deploy"

    # Custom save to set created_by for AssetHistory inline instances
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()


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

    # Custom save to allow setting of read only created_by field.
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    pass

admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetHistory, AssetHistoryAdmin)