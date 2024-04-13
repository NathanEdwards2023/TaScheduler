from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def courseManagement(request):
    return render(request, 'courseManagement.html')