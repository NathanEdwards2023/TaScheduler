from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def courseManagement(request):
    return render(request, 'courseManagement.html')

def createAccount(request):
    #Stub method, complete later
    return render(request, 'createAccount.html')
