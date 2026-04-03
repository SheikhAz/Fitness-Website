from django.contrib.auth.decorators import login_required
from .models import Attendence
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_log, logout
from django.contrib.auth.models import User
from AuthFit.models import Contact, Enrollment, MembershipPlan, Trainer,Attendence
import calendar
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .attendance import mark_attendance
from cloudinary.utils import cloudinary_url
from django.contrib.auth.decorators import user_passes_test




# Create your views here.

# ==============================
# 🔐 STAFF CHECK
# ==============================
def is_staff(user):
    return user.is_staff or user.is_superuser


# ==============================
# ✅ SAVE EMBEDDING (STAFF ONLY)
# ==============================
@csrf_exempt
def save_embedding(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # 🔐 API SECURITY
            API_KEY = "mysecret123"
            if data.get("api_key") != API_KEY:
                return JsonResponse({"error": "Unauthorized"})

            unique_id = data.get("unique_id")
            embedding = data.get("embedding")

            if not unique_id or not embedding:
                return JsonResponse({"error": "Missing data"})

            enrollment = Enrollment.objects.get(unique_id=unique_id)

            # 🔥 CONVERT STRING → LIST
            new_emb = json.loads(embedding)

            # 🔥 INIT LIST IF EMPTY
            if not enrollment.face_embeddings:
                enrollment.face_embeddings = []

            # 🔥 LIMIT MAX EMBEDDINGS (IMPORTANT)
            MAX_EMB = 7
            if len(enrollment.face_embeddings) >= MAX_EMB:
                enrollment.face_embeddings.pop(0)  # remove oldest

            # 🔥 ADD NEW EMBEDDING
            enrollment.face_embeddings.append(new_emb)

            enrollment.face_enrolled = True
            enrollment.save()

            return JsonResponse({
                "status": "success",
                "total_embeddings": len(enrollment.face_embeddings)
            })

        except Enrollment.DoesNotExist:
            return JsonResponse({"error": "User not found"})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request"})

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
            return redirect('/login/')
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
            return redirect('/signup/')

        User.objects.create_user(
            username=username,
            password=password,
        )
        messages.success(request, "Account is created Successfully......")
        return redirect('/login/')
    return render(request, 'authenication/signup.html')


@csrf_exempt
def mark_attendance_api(request):
    if request.method == "POST":
        import json

        try:
            data = json.loads(request.body)

            API_KEY = "mysecret123"
            if data.get("api_key") != API_KEY:
                return JsonResponse({"error": "Unauthorized"})

            unique_id = data.get("unique_id")

            result = mark_attendance(unique_id)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request"})


# ==============================
# 👥 GET USERS (BONUS IMPROVEMENT)
# ==============================
def get_users(request):
    users = Enrollment.objects.filter(face_embeddings__isnull=False)

    data = []

    for u in users:
        data.append({
            "unique_id": u.unique_id,
            "name": u.fullname,
            "embeddings": u.face_embeddings
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
def upload_face_image(request):
    if request.method == "POST":
        try:
            api_key = request.POST.get("api_key")
            if api_key != "mysecret123":
                return JsonResponse({"error": "Unauthorized"})

            unique_id = request.POST.get("unique_id")
            face_image = request.FILES.get("face_image")

            if not unique_id or not face_image:
                return JsonResponse({"error": "Missing data"})

            enrollment = Enrollment.objects.get(unique_id=unique_id)
            enrollment.face_image = face_image  # Cloudinary handles upload automatically
            enrollment.save()

            return JsonResponse({"status": "success", "image_url": enrollment.face_image.url})

        except Enrollment.DoesNotExist:
            return JsonResponse({"error": "User not found"})
        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request"})

def homePage(request):
    enrolled = False
    isStaff = False
    isSuperuser = False

    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user).exists()
        isStaff = request.user.is_staff
        isSuperuser = request.user.is_superuser


    return render(request, "home.html", {
        "enrolled": enrolled,
        "isStaff": isStaff,
        "isSuperuser":isSuperuser,
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
            return redirect('/contact/')

        query = Contact(name=name, email=email, phonenumber=number,
                        description=message)
        query.save()
        messages.success(
            request, "Thanks for Contacting us we will get back you soon")
        return redirect('/contact/')
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
        return redirect('/profile/')

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
            reference=reference,
            address=address,
            user=request.user,
        )
        enroll.save()

        messages.success(
            request,
            "Welcome aboard! Your gym membership has been successfully activated."
        )
        return redirect('/profile/')

    return render(request, 'enrollment.html', {
        "plans": plans,
        "trainers": trainers
    })


def workout(request):
    return render(request, 'workout.html')


@login_required
def Profile(request):
    enrollment = Enrollment.objects.filter(user=request.user).first()

    image_url = None

    if enrollment and enrollment.face_image:
        image_url, _ = cloudinary_url(
            enrollment.face_image.public_id,
            width=300,
            height=300,
            crop="fill"
        )

    return render(request, 'profile.html', {
        'enrollment': enrollment,
        'image_url': image_url
    })


def attendence(request):

    today = timezone.localdate()
    user = request.user

    already_mark = Attendence.objects.filter(
        user=user,
        date=today
    ).exists()

    if request.method == "POST":
        obj, created = Attendence.objects.get_or_create(
            user=user,
            date=today
        )

        if created:
            messages.success(request, "Attendance Successfully Marked.")
        else:
            messages.error(request, "Attendance already marked today.")

        return redirect('/attendence/')

    attendence = Attendence.objects.filter(user = user).order_by('-date')
    attended= Attendence.objects.filter(user = user).order_by('-date')[:7]
    
    

    total_days = attendence.count()
    monthly_days = calendar.monthrange(today.year ,today.month)[1]

    return render(request, 'attendence.html', {
        'already_mark': already_mark,
        'attended':attended,
        'total_days':total_days,
        'monthly_days':monthly_days,
        'today':today
    })
