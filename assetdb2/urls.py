from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.admin import site
import adminactions.actions as actions


actions.add_to_site(site)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'assetdb2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('assets.urls')),
    (r'^adminactions/', include('adminactions.urls')),
)
