from django.db import models, transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from models import AssetHistory
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from .forms import *
from .filters import *
from django.shortcuts import render
from django.core.urlresolvers import reverse
import reversion

# TODO Explore further customisations https://docs.djangoproject.com/en/1.8/intro/tutorial02/#customizing-your-application-s-templates

# TODO Add "Edit" button to toggle 'readonly' attribute for certain fields in change_form.

# TODO Find out why Reversion ignores custom saveformset function override
# https://github.com/etianen/django-reversion/issues/339

# TODO Leave Asset History comment when new asset created via Add Asset.

# TODO Make replace_ipad appear only on iPad pages

# TODO appear to be working efficiently


# Inline for displaying asset history on Asset admin page.
class HistoryInline(admin.StackedInline):
    model = AssetHistory
    verbose_name = 'Asset History'
    verbose_name_plural = 'Asset History'
    can_delete = False
    template = 'admin/assets/assethistory/edit_inline/stacked.html'
    fields = ('notes', )
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


# TODO Simplify admin message construction using string interpolation
class AssetAdmin(DjangoObjectActions, reversion.VersionAdmin, admin.ModelAdmin):
    """
    AssetAdmin
    """

    # Insert custom CSS
    class Media:
        css = {
            'all': ('assets/css/history.css',)
        }

#   For custom change_form template (i.e. override title etc)
    # change_form_template = 'admin/assets/asset/change_form.html'
    change_list_template = 'admin/assets/asset/change_list.html'

    form = AssetAdminForm

    search_fields = ['name', 'serial', 'model', 'manufacturer', 'exact_location', 'owner', 'wired_mac', 'wireless_mac', 'bluetooth_mac']
    list_display = ('name', 'model', 'owner', 'serial', 'wireless_mac', 'location', 'exact_location', 'active', 'purchase_date')
    list_filter = (ActiveListFilter, ModelListFilter, PurchaseYearListFilter, 'far_asset')
    fieldsets = (
        (None, {
            'fields': (('name', 'owner', 'active'),
                       ('location', 'exact_location', 'ip_address'),
                       ('serial', 'model', 'manufacturer', ),
                       ('wired_mac', 'wireless_mac', 'bluetooth_mac'))
        }),
        ('Financial', {
            'fields': (('far_asset', 'far_cost', 'ed_cost'), ('purchase_date', 'warranty_period', 'invoices'))
        }),

    )

    # readonly_fields = ('name',) # TODO Make readonly only on the change_form page. Must be editable on add asset.

    # save_on_top = True
    actions = ['decommission', 'deploy', 'return_ict']
    objectactions = ('replace_ipad', 'decommission', 'return_ict', 'deploy',)
    inlines = [
        HistoryInline,
    ]

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetResource

    # Custom save to set created_by for AssetHistory inline instances
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()

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

                        ah.save()

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
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
            if not queryset[0].active and len(queryset) == 1:
                self.message_user(request, "This asset has already been deactivated.",
                                  level=messages.ERROR)
                return
            else:
                # Create a new decommission form
                form = AssetDecommissionForm()

        # Render the response to the http request
        return render(request, 'admin/assets/decommission.html',
                      {'objects': queryset, 'form': form})

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

                    if asset.active and asset.owner.lower() == 'ict services':
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
                        asset.exact_location = form.cleaned_data['exact_location']
                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident=form.cleaned_data['deploy_to'],
                                          recipient=form.cleaned_data['recipient'],
                                          transfer='internal',
                                          notes=notes)

                        ah.save()

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            reversion.set_user(request.user)
                            reversion.set_comment(notes)
                    else:
                        if not asset.active:
                            currently_inactive += 1
                        elif asset.owner.lower() != 'ict services':
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
            if len(queryset) == 1:
                if not queryset[0].active:
                    self.message_user(request, "You cannot deploy an inactive asset.",
                                      level=messages.ERROR)
                    return
                elif queryset[0].owner.lower() != 'ict services':
                    self.message_user(request, "This asset is not owned by ICT Services. "
                                               "You must return to ICT before deploying again.",
                                      level=messages.ERROR)
                    return

            # Create a new deployment form
            form = AssetDeploymentForm()

        # Render the empty form on a new page passing selected assets and form object fields as dictionaries
        return render(request, 'admin/assets/deploy.html',
                      {'objects': queryset, 'form': form})

    @takes_instance_or_queryset
    def replace_ipad(self, request, queryset):

        if 'cancel' in request.POST:
            self.message_user(request, "Replacement cancelled.", level=messages.ERROR)
            return

        elif 'replace' in request.POST:

            form = iPadReplacementForm(data=request.POST)

            if form.is_valid():
                old_asset = queryset[0]
                # Model specification already prevents assets with the same name. Check anyway!
                new_asset, created = Asset.objects.get_or_create(name=form.cleaned_data['name'])

                if not created:
                    self.message_user(request, "New asset " + new_asset.__str__() + " already exists!",
                                      level=messages.ERROR)
                else:
                    new_asset.manufacturer = form.cleaned_data['manufacturer']
                    new_asset.model = form.cleaned_data['model']
                    new_asset.serial = form.cleaned_data['serial']
                    new_asset.location = 'ccgs'
                    new_asset.exact_location = 'ICT Services'
                    new_asset.owner = 'ICT Services'
                    new_asset.purchase_date = form.cleaned_data['purchase_date']
                    new_asset.invoices = ''
                    new_asset.wired_mac = ''
                    new_asset.wireless_mac = form.cleaned_data['wireless_mac']
                    new_asset.bluetooth_mac = form.cleaned_data['bluetooth_mac']
                    new_asset.far_asset = True
                    new_asset.far_cost = form.cleaned_data['far_cost']
                    new_asset.ed_cost = form.cleaned_data['ed_cost']
                    new_asset.warranty_period = form.cleaned_data['warranty_period']
                    new_asset.ip_address = ''
                    new_asset.active = True

                    old_ah = AssetHistory(asset=old_asset,
                                          created_by=request.user,
                                          incident='general',
                                          recipient='ICT Services',
                                          transfer='internal',
                                          notes='Replaced in stock by %s (%s)' % (new_asset.name, new_asset.serial))

                    new_ah = AssetHistory(asset=new_asset,
                                          created_by=request.user,
                                          incident='general',
                                          recipient='ICT Services',
                                          transfer='incoming',
                                          notes='Received as replacement for %s (%s)' %
                                                (old_asset.name, old_asset.serial))

                    old_ah.save()
                    new_ah.save()

                    # Save model changes and create reversion instance
                    with transaction.atomic(), reversion.create_revision():
                        new_asset.save()
                        reversion.set_user(request.user)
                        reversion.set_comment('Received as replacement for %s (%s)' %
                                              (old_asset.name, old_asset.serial))

                    # TODO Add link to new asset in message
                    self.message_user(request,
                                      "Successfully replaced " + old_asset.__str__() + " with " + new_asset.__str__(),
                                      level=messages.SUCCESS)

                # Use HttpResponseRedirect("../%s" % obj.id]) to redirect to an individual asset change_form
                return HttpResponseRedirect(reverse("admin:assets_asset_changelist"))

        else:
            if len(queryset) > 1:
                self.message_user(request, "This action cannot be applied to multiple assets.", level=messages.ERROR)
                return
            elif queryset[0].active:
                self.message_user(request, "You cannot replace an active asset. Decommission it first.", level=messages.ERROR)
                return
            else:
                old_asset = queryset[0]
                form = iPadReplacementForm(initial={'purchase_date': old_asset.purchase_date,
                                                    'ed_cost': old_asset.ed_cost,
                                                    'far_cost': old_asset.far_cost,
                                                    'warranty_period': old_asset.warranty_period})

        return render(request, 'admin/assets/replace_ipad.html',
                      {'objects': queryset, 'form': form})


    @takes_instance_or_queryset
    def return_ict(self, request, queryset):

        # Prepare message string variables
        rows_updated = len(queryset)
        currently_inactive = 0
        error_bit = ""

        if len(queryset) == 1 and not queryset[0].active:
            self.message_user(request, "You cannot return an inactive asset.", level=messages.ERROR)
            return
        else:
            for asset in queryset:
                # TODO Add logic (and appropriate error messaging) for when an asset is already owned by ICT Services
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

                    ah.save()

                    # Save model changes and create reversion instance
                    with transaction.atomic(), reversion.create_revision():
                        asset.save()
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

    # Names for django action tools
    decommission.short_description = "Decommission selected assets"
    decommission.label = "Decommission"

    deploy.short_description = "Deploy selected assets"
    deploy.label = "Deploy"

    return_ict.short_description = "Return selected assets"
    return_ict.label = "Return to ICT"

    replace_ipad.short_description = "Replace iPads"
    replace_ipad.label = "Replace iPad"


# For importing and exporting Asset History data
class AssetHistoryResource(resources.ModelResource):

    class Meta:
        model = AssetHistory


class AssetHistoryAdmin(ImportExportModelAdmin):
    """
    AssetHistoryAdmin
    """

    list_display = ('asset', 'incident', 'created_by', 'created_date', 'notes')
    search_fields = ['asset__name', 'notes', 'created_by__username']

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetHistoryResource

    # Custom save to allow setting of read only created_by field.
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    pass

admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetHistory, AssetHistoryAdmin)