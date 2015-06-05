from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404

from .forms import AssetDecommissionForm
from .models import Asset


# TODO Create a view for the Asset object. https://docs.djangoproject.com/en/1.8/intro/tutorial03/


def browse(request):

    return render(request, 'browse.html', {})