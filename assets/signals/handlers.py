from django.db.models.signals import pre_save
from django.dispatch import receiver
import reversion
from assets.models import Asset, AssetHistory

# TODO Find a way to create an AssetHistory entry when changes are made. Need to somehow access request.user? Impossible?

@receiver(reversion.pre_revision_commit)
def comment_asset_changes(instances, versions, revision, **kwargs):
    """
        Based on bottom answer from:
        http://stackoverflow.com/questions/12960258/django-check-diference-between-old-and-new-value-when-overriding-save-method

        Catches all reversion saves and leaves a comment with what changed.
    """

    current_version = versions[0].field_dict
    field_list = current_version.keys()
    field_list.remove('id')
    revision_comment = ""

    try:
        past_version = reversion.get_for_object(instances[0])[0].field_dict
    except IndexError:
        # Object created
        if isinstance(instances[0], Asset):
            revision_comment = "%s added to inventory" % current_version['name']
            revision.comment = revision_comment
            ah = AssetHistory(asset=instances[0],
                              created_by=revision.user,
                              incident='general',
                              recipient='ICT Services',
                              transfer='incoming',
                              notes=revision_comment)
            ah.save()

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
                past_test = past_version[field]
            except KeyError:
                # New field created
                pass
            else:
                if current_version[field] != past_test:

                    past_value = past_test
                    if past_value == "":
                        past_value = "[empty]"
                    else:
                        past_value = "\'" + past_value + "\'"

                    new_value = current_version[field]
                    if new_value == "":
                        new_value = "[empty]"
                    else:
                        new_value = "\'" + new_value + "\'"

                    # Get friendly field names for the
                    verbose_field = type(instances[0])._meta.get_field_by_name(field)[0].verbose_name
                    if field != 'edited_date':
                        revision_comment += ", %s: %s > %s" % (verbose_field, past_value, new_value)
                else:
                    pass
        if revision_comment != "":
            revision_comment = "Changes -- %s" % revision_comment[1:]

            if isinstance(instances[0], Asset):
                ah = AssetHistory(asset=instances[0],
                                  created_by=revision.user,
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


# Django signal example
@receiver(pre_save, sender=Asset)
def my_handler(sender, **kwargs):
    """
         https://docs.djangoproject.com/en/1.8/topics/signals/
         http://stackoverflow.com/questions/2719038/where-should-signal-handlers-live-in-a-django-project
         http://www.koopman.me/2015/01/django-signals-example/

    """
    pass