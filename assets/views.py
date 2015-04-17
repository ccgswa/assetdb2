from django.shortcuts import render

# Create your views here.

#TODO Create a view for the Asset object. https://docs.djangoproject.com/en/1.8/intro/tutorial03/

def browse(request):

    return render(request,'assets/browse.html',{})