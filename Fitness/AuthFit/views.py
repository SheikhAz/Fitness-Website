from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate ,login as auth_log
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def loginPage(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request , username = phone ,password=password)
        if user is not None:
            auth_log(request ,user)
            return redirect('/')
        else:
            messages.error(request ,"Invalid Phone or Password ")
            return redirect('/login')
    return render(request , 'authenication/login.html')

def signupPage(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        username = phone
        # Checking the Password.
        if password != confirm_password:
            messages.error(request,"Password Do not Match")
            return redirect('/signup')
        # if User Already Exist in the Database
        if User.objects.filter(first_name = phone).exists():
            messages.error(request , "Phone Number is Already Used By Other User")
            return redirect('/signup')
        
        User.objects.create_user(
            username = username,
            password=password,
        )
        messages.success(request,"Account is created Successfully......")
        return redirect('/login')
    return render(request , 'authenication/signup.html')

def homePage(request):
    return render(request , 'home.html')
def workout(request):
    return render(request , 'workout.html')

@login_required
def Profile(request):
    return render(request , 'profile.html')