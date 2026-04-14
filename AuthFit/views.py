from django.contrib.auth.decorators import login_required
from .models import Attendence
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_log, logout
from django.contrib.auth.models import User
from AuthFit.models import Contact, Enrollment, MembershipPlan, Trainer, Attendence, GymNotification
import calendar
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .attendance import mark_attendance
from cloudinary.utils import cloudinary_url
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from AuthFit.rate_limit import check_login_attempt, reset_attempt
from .forms import UserLogin



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
def save_embeddings_batch(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        if data.get("api_key") != "mysecret123":
            return JsonResponse({"error": "Unauthorized"}, status=403)

        unique_id = data.get("unique_id")
        embeddings = data.get("embeddings", [])

        if not unique_id or not embeddings:
            return JsonResponse({"error": "Missing data"}, status=400)

        enrollment = Enrollment.objects.get(unique_id=unique_id)

        if not enrollment.face_embeddings:
            enrollment.face_embeddings = []

        MAX_EMB = 7
        for emb in embeddings:
            if len(enrollment.face_embeddings) >= MAX_EMB:
                enrollment.face_embeddings.pop(0)
            enrollment.face_embeddings.append(emb)

        enrollment.face_enrolled = True
        enrollment.save()

        return JsonResponse({
            "status": "success",
            "total_embeddings": len(enrollment.face_embeddings)
        })

    except Enrollment.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # Take the FIRST IP — that's the real client
        ip = forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def signupPage(request):
    if request.method == "POST":
        form = UserLogin(request.POST)
        if form.is_valid():
            user = form.save()
            auth_log(request, user)  # log them in immediately
            messages.success(request, "Account created successfully!")
            return redirect('/')
    else:
        form = UserLogin()
    return render(request, 'registration/signup.html', {'form': form})


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/')  # ✅ grab next

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_log(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect(next_url or '/')  # ✅ redirect to next
        else:
            messages.error(request, "Incorrect phone number or password.")
            return redirect('/login/')

    return render(request, 'registration/login.html')

def cache_debug(request):
    cache.set("test_key", "working", timeout=30)
    val = cache.get("test_key")
    return JsonResponse({
        "cache_backend": str(type(cache._cache)),
        "test_value": val,
    })

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
    data = cache.get("face_users")
    if data is None:
        # Build the list from DB
        enrollments = Enrollment.objects.filter(face_embeddings__isnull=False)
        data = []
        for u in enrollments:
            data.append({
                "unique_id": u.unique_id,
                "name": u.fullname,
                "embeddings": u.face_embeddings
            })
        cache.set("face_users", data, timeout=300)  # ← save data, not users
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
            cache.delete(f"profile_image_{enrollment.user.id}")
            cache.delete(f"enrollment_{enrollment.user.id}")

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

    gym_notifications = cache.get("notifications")
    if gym_notifications is None:
        gym_notifications = list(
            GymNotification.objects.filter(is_active=True)
            .values("icon", "message")
        )
        cache.set("notifications", gym_notifications, timeout=3600)

    if request.user.is_authenticated:
        # ✅ Set staff/superuser flags HERE inside the authenticated block
        isStaff = request.user.is_staff
        isSuperuser = request.user.is_superuser

        enrolled = cache.get(f"enrolled_{request.user.id}")
        if enrolled is None:
            enrolled = Enrollment.objects.filter(user=request.user).exists()
            cache.set(f"enrolled_{request.user.id}", enrolled, timeout=300)

    return render(request, "home.html", {
        "enrolled": enrolled,
        "isStaff": isStaff,
        "isSuperuser": isSuperuser,
        "gym_notifications": gym_notifications,
    })

def stats_api(request):
    total_users = Enrollment.objects.count()
    return JsonResponse({"total_users": total_users})

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

        # ✅ Clear cache so profile shows fresh data
        cache.delete(f"enrollment_{request.user.id}")
        cache.delete(f"profile_image_{request.user.id}")
        cache.delete(f"enrolled_{request.user.id}")

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
    cache_key = f"profile_image_{request.user.id}"

    enrollment = cache.get(f"enrollment_{request.user.id}")
    if enrollment is None:
        enrollment = Enrollment.objects.filter(user=request.user).first()
        cache.set(f"enrollment_{request.user.id}", enrollment, timeout=300)

    image_url = cache.get(cache_key)
    if image_url is None and enrollment and enrollment.face_image:
        image_url, _ = cloudinary_url(
            enrollment.face_image.public_id,
            width=130, height=130,  # match actual display size
            crop="fill"
        )
        cache.set(cache_key, image_url, timeout=300)  # cache 5 mins

    return render(request, 'profile.html', {
        'enrollment': enrollment,
        'image_url': image_url,
        'is_expired': enrollment.is_expired if enrollment else False,
        'days_remaining': enrollment.days_remaining if enrollment else 0,
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

    all_attended = list(Attendence.objects.filter(user=user).order_by('-date'))
    attended = all_attended[:7]
    total_days = len(all_attended)
    monthly_days = calendar.monthrange(today.year ,today.month)[1]

    return render(request, 'attendence.html', {
        'already_mark': already_mark,
        'attended':attended,
        'total_days':total_days,
        'monthly_days':monthly_days,
        'today':today
    })
