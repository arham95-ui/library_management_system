from django.urls import path
from django.shortcuts import render

app_name = 'core'

def home(request):
    return render(request, 'core/home.html')

urlpatterns = [
    path('', home, name='home'),
]
