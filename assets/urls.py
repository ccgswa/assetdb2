__author__ = 'gnolan'
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.browse),
]
