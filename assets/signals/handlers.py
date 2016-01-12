# from django.db.models.signals import pre_save
from django.dispatch import receiver
import reversion
from assets.models import Asset, AssetHistory
from django.contrib.auth.models import User


# Reversion signals should not be invoked with the 'sender' attribute
@receiver(reversion.pre_revision_commit)
def comment_asset_changes(instances, versions, revision, **kwargs):
    """
        Based on last answer from:
        http://stackoverflow.com/questions/12960258/django-check-diference-between-old-and-new-value-when-overriding-save-method

        Catches all reversion saves and leaves a comment with what changed.

        Currently only works for individual changes to assets. Fix for mass update


        After importing assets with import/export must run ./manage.py createinitialrevisions assets.asset
    """

    current_version = versions[0].field_dict
    field_list = current_version.keys()
    field_list.remove('id')
    revision_comment = ""
    import_flag = False
    if revision.user is not None:
        revision_user = revision.user
    else:
        revision_user = User.objects.get(username__iexact='root')
        import_flag = True



    try:
        past_version = reversion.get_for_object(instances[0])[0].field_dict # Only checks the first object!!
    except IndexError:
        # No previous revisions for object. Therefore object created.
        if isinstance(instances[0], Asset):  # Assumed that all objects in the revision will be of the same type!

            if len(instances) > 1:
                revision_comment = "Added to inventory by mass import."
            else:
                revision_comment = "%s added to inventory" % current_version['name']

                if import_flag:
                    revision_comment = "%s by mass import" % revision_comment

                ah = AssetHistory(asset=instances[0],
                                  created_by=revision_user,
                                  incident='general',
                                  recipient='ICT Services',
                                  transfer='incoming',
                                  notes=revision_comment)
                ah.save()

            revision.comment = revision_comment


        elif isinstance(instances[0], AssetHistory):
            revision.comment = "New history entry: %s" % current_version['notes']
        else:
            pass
    except TypeError:
        # Object deleted
        pass
    else:
        for field in field_list:
            try:
                past_value = past_version[field]
            except KeyError:
                # New field created that doesn't exist in previous version of object. May occur after model changes.
                pass
            else:
                if current_version[field] != past_value:

                    past_value = blank_to_empty(past_value)
                    new_value = blank_to_empty(current_version[field])

                    # Get friendly field names for the model in question
                    verbose_field = type(instances[0])._meta.get_field_by_name(field)[0].verbose_name
                    if field != 'edited_date':
                            revision_comment += ", %s: %s > %s" % (verbose_field, past_value, new_value)
                else:
                    pass

        if revision_comment != "":
            revision_comment = "Changes -- %s" % revision_comment[1:]

            if isinstance(instances[0], Asset):
                ah = AssetHistory(asset=instances[0],
                                  created_by=revision_user,
                                  incident='general',
                                  recipient='ICT Services',
                                  transfer='incoming',
                                  notes=revision_comment)
                ah.save()
        else:
            revision_comment = "No changes made."

        revision.comment = revision_comment

    revision = revision
    revision.save()



def blank_to_empty(value):
    value = str(value)
    if value == "":
        return "[empty]"
    else:
        return "\'" + value + "\'"