from django.apps import AppConfig


class AssetsConfig(AppConfig):
    """
         https://docs.djangoproject.com/en/1.8/topics/signals/
         http://stackoverflow.com/questions/2719038/where-should-signal-handlers-live-in-a-django-project
         http://www.koopman.me/2015/01/django-signals-example/

    """

    name = 'assets'
    verbose_name = 'Asset Admin'

    def ready(self):
        import assets.signals.handlers