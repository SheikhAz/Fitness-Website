from django.shortcuts import render

# Create your views here.
def loginPage(request):
    return render(request , 'authenication/login.html')

def signupPage(request):
    return render(request , 'authenication/signup.html')

def homePage(request):
    return render(request , 'home.html')