from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the Ecolution index")

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')