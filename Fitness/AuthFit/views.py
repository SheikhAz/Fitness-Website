from datetime import date
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_log, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from AuthFit.models import Contact, Enrollment, MembershipPlan, Trainer, Gallery


# Create your views here.


def loginPage(request):
    if request.method == "POST":
        phone = request.POST.get('usernumber')
        password = request.POST.get('password')

        user = authenticate(request, username=phone, password=password)
        if user is not None:
            auth_log(request, user)
            return redirect('/')
        else:
            messages.error(request, "Invalid Phone or Password ")
            return redirect('/login')
    return render(request, 'authenication/login.html')


def signupPage(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        username = phone
        # Checking that Number is Valid or Not.
        if len(username) > 10 or len(username) < 10:
            messages.error(request, "Phone Number Must be 10 Digits")
            return redirect('/signup')
        # Checking the Password.
        if password != confirm_password:
            messages.error(request, "Password Do not Match")
            return redirect('/signup')
        # if User Already Exist in the Database
        if User.objects.filter(username=phone).exists():
            messages.error(
                request, "Phone Number is Already Used By Other User")
            return redirect('/signup')

        User.objects.create_user(
            username=username,
            password=password,
        )
        messages.success(request, "Account is created Successfully......")
        return redirect('/login')
    return render(request, 'authenication/signup.html')


def homePage(request):
    enrolled = False

    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user).exists()

    return render(request, "home.html", {
        "enrolled": enrolled
    })


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        number = request.POST.get('number')
        email = request.POST.get('email')
        message = request.POST.get('description')

        # Checking that Phone Number is 10 digits only

        if len(number) > 10 or len(number) < 10:
            messages.error(request, "Please Enter a Valid Number")
            return redirect('/contact')

        query = Contact(name=name, email=email, phonenumber=number,
                        description=message)
        query.save()
        messages.success(
            request, "Thanks for Contacting us we will get back you soon")
        return redirect('/contact')
    return render(request, 'contact.html')


def handlelogout(request):
    logout(request)
    messages.success(request, "Logout Successfully......")
    return redirect('/')


@login_required
def enrollment(request):
    plans = MembershipPlan.objects.all()
    trainers = Trainer.objects.all()

    # If user already has enrollment
    if Enrollment.objects.filter(user=request.user).exists():
        return redirect('/profile')

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        plan_id = request.POST.get('plan')
        trainer = request.POST.get('trainer')
        selected_trainer = None
        if trainer:
            selected_trainer = Trainer.objects.get(id=trainer)
        reference = request.POST.get('reference')
        address = request.POST.get('address')

        selected_plan = MembershipPlan.objects.get(id=plan_id)

        enroll = Enrollment(
            fullname=name,
            email=email,
            phone=phone,
            dob=dob,
            selectPlan=selected_plan,
            trainer=selected_trainer,
            gender=gender,
            Reference=reference,
            address=address,
            user=request.user,
        )
        enroll.save()

        messages.success(
            request,
            "Welcome aboard! Your gym membership has been successfully activated."
        )
        print("GENDER:", request.POST.get('gender'))
        return redirect('/profile')

    return render(request, 'enrollment.html', {
        "plans": plans,
        "trainers": trainers
    })


def workout(request):
    return render(request, 'workout.html')


@login_required
def Profile(request):
    enrollment = Enrollment.objects.filter(user=request.user).first()

    return render(request, 'profile.html', {
        'enrollment': enrollment
    })


def gallery(request):
    posts = Gallery.objects.all().order_by("-timestamp")
    return render(request, "gallery.html", {
        "posts": posts
    })


def attendence(request):
    return render(request, 'attendence.html')
