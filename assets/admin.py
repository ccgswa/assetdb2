from django.db import models, transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from models import AssetHistory
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin, ImportExportMixin
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from .forms import *
from .filters import *
from .helpers import *
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
import reversion
from .signals import handlers
import csv

# TODO Add "Edit" button to toggle 'readonly' attribute for certain fields in change_form.

# TODO Find out why Reversion ignores custom saveformset function override
# https://github.com/etianen/django-reversion/issues/339

# TODO appear to be working efficiently

# TODO Integrate django adminactions mass update with reversion


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
        # exclude = ('id', )
        widgets = {
            'purchase_date': {'format': '%Y-%m-%d'},
            }

#    def after_save_instance(self, instance, dry_run): # Does not work with current signal handler configuration.
#        if not dry_run:
#            reversion.set_comment("Added to inventory by mass import.")


# TODO Simplify admin message construction using string interpolation
class AssetAdmin(DjangoObjectActions, reversion.VersionAdmin, ExportActionModelAdmin, ImportExportModelAdmin, admin.ModelAdmin):
    """
    AssetAdmin
    """

    # Insert custom CSS
    class Media:
        css = {
            'all': ('assets/css/history.css',
                    'assets/css/object-action-buttons.css')
        }

#   For custom change_form template (i.e. override title etc)
    change_form_template = 'admin/assets/asset/change_form.html'
    change_list_template = 'admin/assets/asset/change_list.html'

    form = AssetAdminForm

    list_per_page = 500
    search_fields = ['name', 'serial', 'model', 'manufacturer', 'owner', 'wired_mac', 'wireless_mac', 'bluetooth_mac']
    list_display = ('name', 'owner', 'model', 'manufacturer', 'serial', 'wireless_mac', 'location', 'active', 'purchase_date', 'far_cost')
    list_filter = (ActiveListFilter, 'far_asset', ModelListFilter, ManufacturerListFilter, PurchaseYearListFilter)
    fieldsets = (
        (None, {
            'fields': (('name', 'serial', 'active'),
                       ('owner', 'location'),
                       ('model', 'manufacturer', 'ip_address'),
                       ('wired_mac', 'wireless_mac', 'bluetooth_mac'))
        }),
        ('Financial', {
            'fields': (('far_asset', 'far_cost', 'ed_cost'), ('purchase_date', 'warranty_period', 'invoices'))
        }),

    )

    readonly_fields = ('active',)  # TODO Make name readonly only on the change_form page. Must be editable on add asset.

    # save_on_top = True
    actions = ['deploy', 'return_ict', 'decommission', 'reactivate', ]
    objectactions = ('reactivate', 'return_ict', 'replace_ipad', 'deploy', 'decommission', )
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

    def response_change(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly changed Asset's change page
        without using reverse"""
        return HttpResponseRedirect("../%s" % obj.id)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly added Asset's change page
        without using reverse"""
        return HttpResponseRedirect("../%s" % obj.id)

    def get_urls(self):
        """Prepend the URL for csvfilter and csvdeploy to the AssetAdmin URLs
        """
        urls = super(AssetAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^csvfilter/$', self.admin_site.admin_view(self.csvfilter)),
            (r'^csvdeploy/$', self.admin_site.admin_view(self.csvdeploy))
        )
        return my_urls + urls

    def get_queryset(self, request):
        """
        Overrides the default get_queryset of AssetAdmin. If csvupload has been posted, process the csv file and
        modify the queryset to show only those assets listed within.
        """
        qs = super(AssetAdmin, self).get_queryset(request)
        if 'csvupload' in request.POST:
            form = AssetCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                f = csv.reader(request.FILES['csvfile'])
                filterassets = []
                for line in f:
                    filterassets.append(line[0])
                qs = Asset.objects.filter(name__in=filterassets)
        return qs

    def get_actions(self, request):
        actions = super(AssetAdmin, self).get_actions(request)

        # Delete unwanted actions
        if 'merge' in actions:
            del actions['merge']
        if 'export_as_fixture' in actions:
            del actions['export_as_fixture']
        if 'export_as_csv' in actions:
            del actions['export_as_csv']
        if 'export_as_xls' in actions:
            del actions['export_as_xls']
        if 'export_delete_tree' in actions:
            del actions['export_delete_tree']

        return actions

    # Selectively display object actions based on asset state
    def get_object_actions(self, request, context, **kwargs):

        objectactions = []

        if 'original' in context:
            asset = context['original']

            if asset is not None:
                if asset.owner.lower() == 'ict services':
                    objectactions.extend(['deploy'])
                else:
                    if asset.active:
                        objectactions.extend(['return_ict'])

                if asset.active:
                    objectactions.extend(['decommission'])
                else:
                    objectactions.extend(['reactivate'])
                    model = asset.model.lower()
                    if 'ipad' in model.split():
                        objectactions.extend(['replace_ipad'])



        return objectactions

    def csvfilter(self, request):
        """
        A simple view under AssetAdmin that generates and posts a form
        with a csv file containing a simple list of asset names
        """
        form = AssetCSVUploadForm()
        return render(request, 'admin/assets/csvupload.html',
                      {'form': form})


    def csvdeploy(self, request):
        """
        Takes a csv file containing asset names in the first column and deploys them to the owner
        in the second column.
        """
        if 'cancel' in request.POST:
            self.message_user(request, 'Mass deployment cancelled.', level=messages.ERROR)
            return

        elif 'csvdeploy' in request.POST:
            # Create form object with submitted data
            form = AssetCSVDeploymentForm(request.POST, request.FILES)

            if form.is_valid():

                f = csv.reader(request.FILES['csvfile'])

                # Prepare message string variables
                rows_updated = 0
                currently_inactive = []
                currently_deployed = []
                does_not_exist = []

                for row in f:
                    rows_updated += 1

                    name = row[0]
                    owner = row[1]

                    try:
                        asset = Asset.objects.get(name=name)  # Should only return one asset. Names are unique!
                    except Asset.DoesNotExist:
                        asset = None

                    # Check for errors before deploying
                    if asset is None:
                        does_not_exist.append(name)

                    elif not asset.active:
                        currently_inactive.append(name)

                    elif asset.owner.lower() != 'ict services':
                        currently_deployed.append(name)

                    else:  # Deploy away!
                        deploy_type = ''
                        if form.cleaned_data['deploy_to'] == 'deploy_staff':
                            deploy_type = 'staff member'
                        elif form.cleaned_data['deploy_to'] == 'deploy_student':
                            deploy_type = 'student'
                        notes = 'Deployed to %s %s' % (deploy_type, owner)
                        asset.location = form.cleaned_data['location']
                        asset.owner = owner
                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident=form.cleaned_data['deploy_to'],
                                          recipient=owner,
                                          transfer='internal',
                                          notes=notes)

                        ah.save()

                        # Disconnect the pre_reversion_commit signal to prevent auto comment
                        reversion.pre_revision_commit.disconnect(handlers.comment_asset_changes)

                        # Set flag to be read by pre_revision_commit handler
                        asset.flag = 'action'

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            reversion.set_user(request.user)
                            reversion.set_comment('Deployed as part of mass csv deployment.')

                        # Reconnect to the signal
                        reversion.pre_revision_commit.connect(handlers.comment_asset_changes)

                rows_updated -= len(currently_inactive) + len(currently_deployed) + len(does_not_exist)

                # Construct messages to user
                if rows_updated == 0:
                    self.message_user(request, "Could not deploy anything. Check the file for errors.",
                                      level=messages.ERROR)
                else:
                    self.message_user(request, "Number of assets deployed: %s" % rows_updated, level=messages.SUCCESS)

                if len(does_not_exist) > 0:
                    self.message_user(request, generate_error_string("Not found: ", does_not_exist),
                                      level=messages.ERROR)

                if len(currently_inactive) > 0:
                    self.message_user(request,
                                      generate_error_string("Could not deploy inactive assets: ", currently_inactive),
                                      level=messages.ERROR)

                if len(currently_deployed) > 0:
                    self.message_user(request, generate_error_string("Already deployed: ",
                                                                     currently_deployed), level=messages.ERROR)

                return HttpResponseRedirect(reverse("admin:assets_asset_changelist"))

        else:
            form = AssetCSVDeploymentForm()
            return render(request, 'admin/assets/csvdeploy.html',
                          {'form': form})


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
                        # asset.exact_location = form.cleaned_data['recipient']
                        asset.owner = '%s - %s' % (asset.owner, form.cleaned_data['location'])
                        asset.active = False
                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident='decommission',
                                          recipient=form.cleaned_data['recipient'],
                                          transfer='outgoing',
                                          notes=form.cleaned_data['notes'])

                        ah.save()

                        # Disconnect the pre_reversion_commit signal to prevent auto comment
                        reversion.pre_revision_commit.disconnect(handlers.comment_asset_changes)

                        # Set flag to tell pre_revision_commit handler to skip processing
                        asset.flag = 'action'

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            reversion.set_user(request.user)
                            reversion.set_comment('Asset decommissioned. Recipient: %s Note: %s' %
                                                  (form.cleaned_data['recipient'],
                                                   form.cleaned_data['notes']))

                        # Reconnect to the signal
                        reversion.pre_revision_commit.connect(handlers.comment_asset_changes)

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

    decommission.attrs = {
        'class': 'red-button',
    }

    # Django Admin action to deploy assets.
    # The django-object-actions decorator makes it available in change_form template.
    @takes_instance_or_queryset
    def deploy(self, request, queryset):

        # The user cancelled. Return to the change list.
        if 'cancel' in request.POST:
            self.message_user(request, 'Deployment cancelled.', level=messages.ERROR)
            return

        # Check that we've submitted the form
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
                        # asset.exact_location = form.cleaned_data['exact_location']
                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident=form.cleaned_data['deploy_to'],
                                          recipient=form.cleaned_data['recipient'],
                                          transfer='internal',
                                          notes=notes)

                        ah.save()

                        # Disconnect the pre_reversion_commit signal to prevent auto comment
                        reversion.pre_revision_commit.disconnect(handlers.comment_asset_changes)

                        # Set flag to be read by pre_revision_commit handler
                        asset.flag = 'action'

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            reversion.set_user(request.user)
                            reversion.set_comment(notes)

                        # Reconnect to the signal
                        reversion.pre_revision_commit.connect(handlers.comment_asset_changes)

                    else:
                        if not asset.active:
                            currently_inactive += 1
                        elif asset.owner.lower() != 'ict services':
                            currently_deployed += 1

                        if (currently_inactive == 1 and currently_deployed == 0) or (currently_inactive == 0 and currently_deployed == 1):
                            error_bit += asset.name
                        else:
                            if asset.owner.lower() != 'ict services':
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
                    self.message_user(request, "%s You must return assets to ICT before deploying again." % error_bit,
                                      level=messages.WARNING)

                return

        # We've submitted a different form (i.e. change list/form). Go to the form.
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

    deploy.attrs = {
        'class': 'purple-button',
    }


    @takes_instance_or_queryset
    def return_ict(self, request, queryset):

        # Prepare message string variables
        rows_updated = len(queryset)
        currently_inactive = 0
        already_returned = 0
        error_bit = ""

        if len(queryset) == 1 and not queryset[0].active:
            self.message_user(request, "You cannot return an inactive asset.", level=messages.ERROR)
            return
        else:
            for asset in queryset:
                # TODO Add logic (and appropriate error messaging) for when an asset is already owned by ICT Services
                if asset.active and asset.owner.lower() != 'ict services':
                    notes = 'Returned to ICT Services by %s' % asset.owner
                    asset.location = 'ccgs'
                    # asset.exact_location = 'ICT Services'
                    asset.owner = 'ICT Services'
                    ah = AssetHistory(asset=asset,
                                      created_by=request.user,
                                      incident='return',
                                      recipient='ICT Services',
                                      transfer='internal',
                                      notes=notes)

                    ah.save()

                    # Disconnect the pre_reversion_commit signal to prevent auto comment
                    reversion.pre_revision_commit.disconnect(handlers.comment_asset_changes)

                    # Set flag to be read by pre_revision_commit handler
                    asset.flag = 'action'

                    # Save model changes and create reversion instance
                    with transaction.atomic(), reversion.create_revision():
                        asset.save()
                        reversion.set_user(request.user)
                        reversion.set_comment(notes)

                    # Reconnect to the signal
                    reversion.pre_revision_commit.connect(handlers.comment_asset_changes)

                else:
                    if not asset.active:
                        currently_inactive += 1
                        if currently_inactive == 1:
                            error_bit += asset.name
                        else:
                            error_bit += ", %s" % asset.name
                    else:
                        already_returned += 1

            rows_updated -= (currently_inactive + already_returned)

            # Construct message to user based on how many assets were updated
            if rows_updated == 0:
                self.message_user(request, "Cannot return inactive assets or assets owned by ICT Services."
                                  , level=messages.ERROR)
            else:
                if rows_updated == 1:
                    message_bit = "%s was" % queryset[0].name
                else:
                    message_bit = "%s assets were" % rows_updated
                self.message_user(request, "%s returned to ICT Services." % message_bit,
                                  level=messages.SUCCESS)

                if already_returned > 0:
                    self.message_user(request, "Some assets were already owned by ICT Services.", level=messages.WARNING)

            # Generate error string
            if currently_inactive > 0:
                if currently_inactive == 1:
                    error_bit += " is inactive."
                elif currently_inactive > 1:
                    error_bit += " are inactive."
                self.message_user(request, "%s Cannot return." % error_bit, level=messages.WARNING)

    return_ict.attrs = {
        'class': 'green-button',
        'onclick': 'return confirm("Return this asset to ICT Services?");',
    }

    # Django Admin action to reactivate a decommissioned asset.
    # The django-object-actions decorator makes it available in change_form template.
    @takes_instance_or_queryset
    def reactivate(self, request, queryset):

        # The user cancelled. Return to the change list.
        if 'cancel' in request.POST:
            self.message_user(request, 'Re-activation cancelled.', level=messages.ERROR)
            return

        # Check that we've submitted the form
        elif 'reactivate_asset' in request.POST:
            # Create form object with submitted data
            form = AssetReactivationForm(request.POST)

            if form.is_valid():

                # Prepare message string variables
                rows_updated = 0
                currently_active = []

                # Use validated data to deploy selected assets
                for asset in queryset:
                    rows_updated += 1

                    if asset.active:
                        currently_active.append(asset.name)
                    else:
                        notes = 'Asset re-activated. Reason: %s' % (form.cleaned_data['reason'])

                        asset.location = 'ccgs'
                        asset.owner = 'ICT Services'
                        asset.active = True

                        ah = AssetHistory(asset=asset,
                                          created_by=request.user,
                                          incident='return',
                                          recipient='ICT Services',
                                          transfer='incoming',
                                          notes=notes)

                        ah.save()

                        # Disconnect the pre_reversion_commit signal to prevent auto comment
                        reversion.pre_revision_commit.disconnect(handlers.comment_asset_changes)

                        # Set flag to be read by pre_revision_commit handler
                        asset.flag = 'action'

                        # Save model changes and create reversion instance
                        with transaction.atomic(), reversion.create_revision():
                            asset.save()
                            reversion.set_user(request.user)
                            reversion.set_comment(notes)

                        # Reconnect to the signal
                        reversion.pre_revision_commit.connect(handlers.comment_asset_changes)

                rows_updated -= len(currently_active)

                # Construct messages to user
                if rows_updated == 0:
                    self.message_user(request, "Active assets cannot be reactivated.",
                                      level=messages.ERROR)
                else:
                    if len(queryset) == 1 and rows_updated == 1:
                        self.message_user(request, "%s was re-activated" % asset.name, level=messages.SUCCESS)
                    else:
                        self.message_user(request, "Number of assets reactivated: %s" % rows_updated, level=messages.SUCCESS)

                    if len(currently_active) > 0:
                        self.message_user(request, generate_error_string("Already active: ", currently_active),
                                          level=messages.ERROR)

                return

        # We've submitted a different form (i.e. change list/form). Go to the form.
        else:
            if len(queryset) == 1:
                if queryset[0].active:
                    self.message_user(request, "This asset is already active.",
                                      level=messages.ERROR)
                    return

            # Create a new deployment form
            form = AssetReactivationForm()

            # Render the empty form on a new page passing selected assets and form object fields as dictionaries
            return render(request, 'admin/assets/reactivate.html',
                          {'objects': queryset, 'form': form})

    reactivate.attrs = {
        'class': 'green-button',
    }


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
                    # new_asset.exact_location = 'ICT Services'
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

                    # Disconnect the pre_reversion_commit signal to prevent auto comment
                    reversion.pre_revision_commit.disconnect(handlers.comment_asset_changes)

                    # Set flag to be read by pre_revision_commit handler
                    new_asset.flag = 'action'

                    # Save model changes and create reversion instance
                    with transaction.atomic(), reversion.create_revision():
                        new_asset.save()
                        reversion.set_user(request.user)
                        reversion.set_comment('Received as replacement for %s (%s)' %
                                              (old_asset.name, old_asset.serial))

                    # Reconnect to the signal
                    reversion.pre_revision_commit.connect(handlers.comment_asset_changes)

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

    replace_ipad.attrs = {
        'class': 'orange-button',
    }


    # Descriptions (user friendly names) for Django admin actions
    decommission.short_description = "Decommission selected assets"
    decommission.label = "Decommission"

    deploy.short_description = "Deploy selected assets"
    deploy.label = "Deploy"

    return_ict.short_description = "Return selected assets to ICT"
    return_ict.label = "Return to ICT"

    replace_ipad.short_description = "Replace iPads"
    replace_ipad.label = "Replace iPad"

    reactivate.short_description = "Re-activate selected assets"
    reactivate.label = "Re-activate"


# For importing and exporting Asset History data
class AssetHistoryResource(resources.ModelResource):

    class Meta:
        model = AssetHistory

#    def after_save_instance(self, instance, dry_run): # Does not work with current signal handler configuration.
#        if not dry_run:
#           reversion.set_comment("Data imported from file.")  #  Comments overridden by signal handler


class AssetHistoryAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ExportActionModelAdmin, admin.ModelAdmin):
    """
    AssetHistoryAdmin
    """

    list_display = ('asset', 'incident', 'created_by', 'created_date', 'notes')
    search_fields = ['asset__name', 'notes', 'created_by__username']
    change_list_template = 'admin/assets/assethistory/change_list.html'

    # Integrate ImportExport functionality for AssetAdmin
    resource_class = AssetHistoryResource

    # Custom save to allow setting of read only created_by field.
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    def response_change(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly changed AssetHistory's change page
        without using reverse"""
        return HttpResponseRedirect("../%s" % obj.id)

    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly added AssetHistory's change page
        without using reverse"""
        return HttpResponseRedirect("../%s" % obj.id)

    def get_actions(self, request):
        actions = super(AssetHistoryAdmin, self).get_actions(request)

        # Delete unwanted actions
        if 'merge' in actions:
            del actions['merge']
        if 'graph_queryset' in actions:
            del actions['graph_queryset']
        if 'export_as_fixture' in actions:
            del actions['export_as_fixture']
        if 'export_as_csv' in actions:
            del actions['export_as_csv']
        if 'export_as_xls' in actions:
            del actions['export_as_xls']
        if 'export_delete_tree' in actions:
            del actions['export_delete_tree']

        return actions

admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetHistory, AssetHistoryAdmin)