from django.db import models, transaction
from django import forms
from django.contrib import admin
from django.contrib import messages
from models import Asset, AssetHistory
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from .forms import *
from django.shortcuts import render
import reversion
import plistlib
from widgets import ExcelDateWidget

# TODO Explore further customisations https://docs.djangoproject.com/en/1.8/intro/tutorial02/#customizing-your-application-s-templates

# TODO Add "Edit" button to toggle 'readonly' attribute for certain fields in change_form.

# TODO Add CSS and JQuery to admin classes using the Media inner class https://docs.djangoproject.com/en/dev/ref/contrib/admin/#modeladmin-asset-definitions


# Inline for displaying asset history on Asset admin page.
class HistoryInline(admin.StackedInline):
    model = AssetHistory
    verbose_name = 'Asset History'
    verbose_name_plural = 'Asset History'
    can_delete = False
    template = 'admin/assets/assethistory/edit_inline/stacked.html'
    fields = ('recipient', 'notes',)
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
    # Excel dates are in floating point format. Accommodate to prevent import errors.
    # See https://github.com/django-import-export/django-import-export/issues/201 for excel date widget. Try that!
    # widget=widgets.DateWidget(format='%d/%m/%Y') ?
    # purchase_date = fields.Field(column_name='purchase_date', widget=ExcelDateWidget('%d/%m/%Y'))

    class Meta:
        model = Asset


class AssetAdmin(DjangoObjectActions, reversion.VersionAdmin, ImportExportModelAdmin):
    """
    AssetAdmin
    """

    # Insert custom CSS
    class Media:
        css = {
            'all': ('assets/css/history.css',)
        }

#   For custom change_form template (i.e. override title etc)
#   change_form_template = 'admin/assets/asset/change_form.html'
    change_list_template = 'admin/assets/asset/change_list.html'

    form = AssetAdminForm

    search_fields = ['name', 'serial', 'wireless_mac']
    list_display = ('name', 'serial', 'owner', 'location', 'exact_location', 'active', 'purchase_date')
#   readonly_fields = ['created_date', 'created_by'] # Don't appear on change_form page. DEPRECATED. USING REVERSION
    fieldsets = (
        (None, {
            'fields': (('name', 'owner', 'active'),
                       ('location', 'exact_location', 'ip_address'),
                       ('serial', 'model', 'manufacturer', ),
                       ('wireless_mac', 'wired_mac', 'bluetooth_mac'))
        }),
        ('Financial', {
            'classes': ('collapse',),
            'fields': (('far_asset', 'far_cost', 'ed_cost'), ('purchase_date', 'warranty_period'))
        }),

    )

    # save_on_top = True
    actions = ['decommission', 'deploy', 'return_ict']
    objectactions = ('decommission', 'replace_ipad', 'return_ict', 'deploy',)
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
                currently_inactive = 0
                error_bit = ""

                # Use validated data to decommission selected assets
                for asset in queryset:
                    if asset.active:
                        asset.location = form.cleaned_data['location']
                        asset.exact_location = form.cleaned_data['recipient']
                        asset.owner = '%s - %s' % (asset.owner, form.cleaned_data['location'])
                        asset.active = False
                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident='decommission',
                                          recipient=form.cleaned_data['recipient'],
                                          transfer='outgoing',
                                          notes=form.cleaned_data['notes'])

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            ah.save()
                            reversion.set_user(request.user)
                            reversion.set_comment('Asset decommissioned. Recipient: %s Note: %s' %
                                                  (form.cleaned_data['recipient'],
                                                   form.cleaned_data['notes']))
                    else:
                        currently_inactive += 1
                        if currently_inactive == 1:
                            error_bit += asset.name
                        else:
                            error_bit += ", %s" % asset.name

                rows_updated -= currently_inactive

                # Construct message to user based on how many assets were updated
                if rows_updated == 0:
                    self.message_user(request, "Cannot decommission inactive assets.", level=messages.ERROR)
                else:
                    if rows_updated == 1:
                        message_bit = "%s was" % queryset[0].name
                    else:
                        message_bit = "%s assets were" % rows_updated
                    self.message_user(request, "%s successfully decommissioned." % message_bit,
                                      level=messages.SUCCESS)

                # Generate error string
                if currently_inactive > 0:
                    if currently_inactive == 1:
                        error_bit += " was already inactive."
                    elif currently_inactive > 1:
                        error_bit += " were already inactive."
                    self.message_user(request, "%s Could not decommission." % error_bit, level=messages.WARNING)

                return

        # We've submitted a different form (i.e. change list/form). Go to the decommission form.
        else:
            # Create a new decommission form
            form = AssetDecommissionForm()

        # Render the response to the http request
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
                currently_inactive = 0
                currently_deployed = 0
                error_bit = ""

                # Use validated data to deploy selected assets
                for asset in queryset:

                    if asset.active and asset.owner == 'ICT Services':
                        notes = ''
                        deploy_type = ''
                        if form.cleaned_data['deploy_to'] == 'deploy_staff':
                            deploy_type = 'staff member'
                        elif form.cleaned_data['deploy_to'] == 'deploy_student':
                            deploy_type = 'student'
                        notes = 'Deployed to %s %s' % (deploy_type, form.cleaned_data['recipient'])
                        if form.cleaned_data['replacing'] != '':
                            notes += ' as replacement for %s' % form.cleaned_data['replacing']
                        asset.location = form.cleaned_data['location']
                        asset.owner = form.cleaned_data['recipient']
                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident=form.cleaned_data['deploy_to'],
                                          recipient=form.cleaned_data['recipient'],
                                          transfer='internal',
                                          notes=notes)

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            ah.save()
                            reversion.set_user(request.user)
                            reversion.set_comment(notes)
                    else:
                        if not asset.active:
                            currently_inactive += 1
                        elif asset.owner != 'ICT Services':
                            currently_deployed += 1

                        if (currently_inactive == 1 and currently_deployed == 0) or (currently_inactive == 0 and currently_deployed == 1):
                            error_bit += asset.name
                        else:
                            error_bit += ", %s" % asset.name

                rows_updated -= currently_inactive + currently_deployed

                # Construct message to user based on how many assets were updated
                if rows_updated == 0:
                    self.message_user(request, "Could not deploy anything.", level=messages.ERROR)
                else:
                    if rows_updated == 1:
                        message_bit = "%s was" % queryset[0].name
                    else:
                        message_bit = "%s assets were" % rows_updated
                    self.message_user(request, "%s successfully deployed to %s" %
                                      (message_bit, form.cleaned_data['recipient']), level=messages.SUCCESS)

                # Generate error string
                if currently_inactive > 0:
                    if currently_inactive == 1:
                        error_bit += " is not active."
                    else:
                        error_bit += " were not active."
                    self.message_user(request, "%s Please reactivate to deploy." % error_bit, level=messages.WARNING)

                if currently_deployed > 0:
                    if currently_deployed == 1:
                        error_bit = " %s has already been deployed to %s." % (asset.name, asset.owner)
                    else:
                        error_bit = " Some assets have already been deployed."
                    self.message_user(request, "%s You must return assets before deploying again." % error_bit,
                                      level=messages.WARNING)

                return

        # We've submitted a different form (i.e. change list/form). Go to the decommission form.
        else:
            # Create a new deployment form
            form = AssetDeploymentForm()
        # Render the empty form on a new page passing selected assets and form object fields as dictionaries
        return render(request, 'admin/assets/deploy.html',
                      {'objects': queryset, 'form': form})

    # TODO Complete/Fix the replace iPad function.
    @takes_instance_or_queryset
    def replace_ipad_multiform(self, request, queryset):

        template = 'admin/assets/replace_ipad1.html'

        if 'cancel' in request.POST:
            self.message_user(request, "Replacement cancelled.", level=messages.ERROR)
            return

        elif 'ipad_config' in request.POST:

            form = AssetReplacementForm1(request.POST)

            if form.is_valid():
                # Process the file data and save the data for use on the second page
                pass

            # Create empty form to pass to render function
            template = 'admin/assets/replace_ipad2.html'
            form = AssetReplacementForm2()
            print 'First form submitted'
            # Don't return

        elif 'replace' in request.POST:

            form = AssetReplacementForm2(request.POST)
            if form.is_valid():
                print 'Second form submitted'
                # Do stuff.
                return

        else:
            form = AssetReplacementForm1()

        return render(request, template,
                      {'objects': queryset, 'form': form})

        # if len(queryset) > 1:
        #     self.message_user(request, "Cannot replace multiple assets. "
        #                                "Try using 'Replace' from an individual asset\'s page.", level=messages.ERROR)
        # else:
        #     pass
        # i = plistlib.readPlist(form['difile'].file)

        # asset = queryset[0]

    # TODO Complete/Fix the replace iPad function.
    @takes_instance_or_queryset
    def replace_ipad(self, request, queryset):

        if 'cancel' in request.POST:
            self.message_user(request, "Replacement cancelled.", level=messages.ERROR)
            return

        elif 'replace' in request.POST:
            form = iPadReplacementForm(data=request.POST, files=request.FILES)

            if form.is_valid():
                old_asset = queryset[0]
                # TODO Complete this section. Check if new asset already exists!
                # new_asset = Asset(name=form.cleaned_data['name'],
                #                   created_by=request.user,
                #                   incident=form.cleaned_data['deploy_to'],
                #                   recipient=form.cleaned_data['recipient'],
                #                   transfer='internal',
                #                   notes=notes)

                new_asset.save();
                self.message_user(request,
                                  "Successfully replaced " + old_asset.__str__() + " with " + new_asset.__str__()
                                  , level=messages.SUCCESS)
                return

        else:
            if len(queryset) > 1:
                self.message_user(request, "This action cannot be applied to multiple assets.", level=messages.ERROR)
                return
            elif queryset[0].active:
                self.message_user(request, "You cannot replace an active asset. Decommission first.", level=messages.ERROR)
                return
            else:
                old_asset = queryset[0]
                form = iPadReplacementForm(initial={'purchase_date': old_asset.purchase_date,
                                                    'ed_cost': old_asset.ed_cost,
                                                    'far_cost': old_asset.far_cost,
                                                    'warranty_period': old_asset.warranty_period,
                                                    'far_asset': True,
                                                    'active': True})

        return render(request, 'admin/assets/replace_ipad.html',
                      {'objects': queryset, 'form': form})


    @takes_instance_or_queryset
    def return_ict(self, request, queryset):

        # Prepare message string variables
        rows_updated = len(queryset)
        currently_inactive = 0
        error_bit = ""

        for asset in queryset:
            # TODO Return: Add logic (and appropriate error messaging) for when an asset is already owned by ICT Services
            if asset.active:
                notes = 'Returned to ICT Services by %s' % asset.owner
                asset.location = 'ccgs'
                asset.exact_location = 'ICT Services'
                asset.owner = 'ICT Services'
                ah = AssetHistory(asset=asset,
                                  created_by=request.user,
                                  incident='return',
                                  recipient='ICT Services',
                                  transfer='internal',
                                  notes=notes)

                # Save model changes and create reversion instance
                with transaction.atomic(), reversion.create_revision():
                    asset.save()
                    ah.save()
                    reversion.set_user(request.user)
                    reversion.set_comment(notes)
            else:
                currently_inactive += 1
                if currently_inactive == 1:
                    error_bit += asset.name
                else:
                    error_bit += ", %s" % asset.name

                rows_updated -= currently_inactive

                # Construct message to user based on how many assets were updated
                if rows_updated == 0:
                    self.message_user(request, "Cannot return inactive assets.", level=messages.ERROR)
                else:
                    if rows_updated == 1:
                        message_bit = "%s was" % queryset[0].name
                    else:
                        message_bit = "%s assets were" % rows_updated
                    self.message_user(request, "%s returned to ICT Services." % message_bit,
                                      level=messages.SUCCESS)

                # Generate error string
                if currently_inactive > 0:
                    if currently_inactive == 1:
                        error_bit += " is inactive."
                    elif currently_inactive > 1:
                        error_bit += " are inactive."
                    self.message_user(request, "%s Cannot return." % error_bit, level=messages.WARNING)

    # Custom save to set created_by for AssetHistory inline instances
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    # Names for django action tools
    decommission.short_description = "Decommission selected assets"
    decommission.label = "Decommission"

    deploy.short_description = "Deploy selected assets"
    deploy.label = "Deploy"

    return_ict.short_description = "Return selected assets"
    return_ict.label = "Return to ICT"

    replace_ipad.short_description = "Replace iPads"
    replace_ipad.label = "Replace iPad"

    pass


# For importing and exporting Asset History data
class AssetHistoryResource(resources.ModelResource):

    class Meta:
        model = AssetHistory


class AssetHistoryAdmin(reversion.VersionAdmin, ImportExportModelAdmin):
    """
    AssetHistoryAdmin
    """

    list_display = ('asset', 'incident', 'created_by', 'created_date', 'notes')
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