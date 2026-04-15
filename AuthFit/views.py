import os
import json
import calendar

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_log, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from cloudinary.utils import cloudinary_url

from AuthFit.models import Contact, Enrollment, MembershipPlan, Trainer, Attendence, GymNotification
from AuthFit.rate_limit import check_login_attempt, reset_attempt
from .attendance import mark_attendance
from .forms import UserLogin
from urllib.parse import urlparse
from AuthFit.rate_limit import check_login_attempt, reset_attempt, record_failed_attempt


# ==============================
# API KEY (from environment)
# ==============================
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "")


# ==============================
# STAFF CHECK
# ==============================
def is_staff(user):
    return user.is_staff or user.is_superuser


# ==============================
# GET CLIENT IP
# ==============================
def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==============================
# SAVE EMBEDDING (STAFF ONLY)
# ==============================
@csrf_exempt
def save_embeddings_batch(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        if not INTERNAL_API_KEY or data.get("api_key") != INTERNAL_API_KEY:
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


# ==============================
# SIGNUP PAGE
# ==============================
def signupPage(request):
    # Redirect already authenticated users
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        form = UserLogin(request.POST)
        if form.is_valid():
            user = form.save()
            auth_log(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('/')
    else:
        form = UserLogin()

    return render(request, 'registration/signup.html', {'form': form})


# ==============================
# LOGIN PAGE
# ==============================
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')

    next_url = request.GET.get('next') or request.POST.get('next', '/')

    if request.method == "POST":
        ip = get_client_ip(request)
        phone = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # ✅ Only check if locked out — don't increment yet
        if not check_login_attempt(ip, phone):
            messages.error(
                request, "Too many failed login attempts. Please try again later.")
            return redirect(f'/login/?next={next_url}')

        user = authenticate(request, username=phone, password=password)

        if user is not None:
            reset_attempt(ip, phone)
            auth_log(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect(_safe_next(next_url, request))
        else:
            record_failed_attempt(ip, phone)   # ✅ Only increment on failure
            messages.error(request, "Incorrect phone number or password.")
            return redirect(f'/login/?next={next_url}')

    return render(request, 'registration/login.html', {'next': next_url})


def _safe_next(next_url: str, request) -> str:
    """
    Allow only same-origin redirects to prevent open-redirect attacks.
    Falls back to '/' for external or malformed URLs.
    """
    parsed = urlparse(next_url)
    if parsed.netloc and parsed.netloc != request.get_host():
        return '/'
    return next_url or '/'


# ==============================
# CACHE DEBUG (dev only)
# ==============================
def cache_debug(request):
    cache.set("test_key", "working", timeout=30)
    val = cache.get("test_key")
    return JsonResponse({
        "cache_backend": str(type(cache._cache)),
        "test_value": val,
    })


# ==============================
# MARK ATTENDANCE API
# ==============================
@csrf_exempt
def mark_attendance_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        if not INTERNAL_API_KEY or data.get("api_key") != INTERNAL_API_KEY:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        unique_id = data.get("unique_id")
        if not unique_id:
            return JsonResponse({"error": "Missing unique_id"}, status=400)

        result = mark_attendance(unique_id)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==============================
# GET USERS (face embeddings)
# ==============================
def get_users(request):
    data = cache.get("face_users")
    if data is None:
        enrollments = Enrollment.objects.filter(face_embeddings__isnull=False)
        data = [
            {
                "unique_id": u.unique_id,
                "name": u.fullname,
                "embeddings": u.face_embeddings,
            }
            for u in enrollments
        ]
        cache.set("face_users", data, timeout=300)
    return JsonResponse(data, safe=False)


# ==============================
# UPLOAD FACE IMAGE
# ==============================
@csrf_exempt
def upload_face_image(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        api_key = request.POST.get("api_key")
        if not INTERNAL_API_KEY or api_key != INTERNAL_API_KEY:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        unique_id = request.POST.get("unique_id")
        face_image = request.FILES.get("face_image")

        if not unique_id or not face_image:
            return JsonResponse({"error": "Missing data"}, status=400)

        enrollment = Enrollment.objects.get(unique_id=unique_id)
        enrollment.face_image = face_image  # Cloudinary handles upload
        enrollment.save()

        cache.delete(f"profile_image_{enrollment.user.id}")
        cache.delete(f"enrollment_{enrollment.user.id}")

        return JsonResponse({"status": "success", "image_url": enrollment.face_image.url})

    except Enrollment.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==============================
# HOME PAGE
# ==============================
def homePage(request):
    enrolled = False
    isStaff = False
    isSuperuser = False

    gym_notifications = cache.get("notifications")
    if gym_notifications is None:
        gym_notifications = list(
            GymNotification.objects.filter(
                is_active=True).values("icon", "message")
        )
        cache.set("notifications", gym_notifications, timeout=3600)

    if request.user.is_authenticated:
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


# ==============================
# STATS API
# ==============================
def stats_api(request):
    total_users = Enrollment.objects.count()
    return JsonResponse({"total_users": total_users})


# ==============================
# CONTACT PAGE
# ==============================
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        number = request.POST.get('number', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('description', '').strip()

        # ✅ Validate: exactly 10 digits, numeric only
        if not number.isdigit() or len(number) != 10:
            messages.error(
                request, "Please enter a valid 10-digit phone number.")
            return redirect('/contact/')

        query = Contact(
            name=name,
            email=email,
            phonenumber=number,
            description=message
        )
        query.save()
        messages.success(
            request, "Thanks for contacting us — we'll get back to you soon!")
        return redirect('/contact/')

    return render(request, 'contact.html')


# ==============================
# LOGOUT
# ==============================
def handlelogout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/')


# ==============================
# ENROLLMENT
# ==============================
@login_required
def enrollment(request):
    # Redirect if already enrolled
    if Enrollment.objects.filter(user=request.user).exists():
        return redirect('/profile/')

    plans = MembershipPlan.objects.all()
    trainers = Trainer.objects.all()

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        plan_id = request.POST.get('plan')
        trainer_id = request.POST.get('trainer')
        reference = request.POST.get('reference', '').strip()
        address = request.POST.get('address', '').strip()

        selected_trainer = None
        if trainer_id:
            try:
                selected_trainer = Trainer.objects.get(id=trainer_id)
            except Trainer.DoesNotExist:
                messages.error(request, "Selected trainer does not exist.")
                return redirect('/enrollment/')

        try:
            selected_plan = MembershipPlan.objects.get(id=plan_id)
        except MembershipPlan.DoesNotExist:
            messages.error(request, "Selected plan does not exist.")
            return redirect('/enrollment/')

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

        # Clear relevant caches
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
        "trainers": trainers,
    })


# ==============================
# WORKOUT PAGE
# ==============================
def workout(request):
    return render(request, 'workout.html')


# ==============================
# 👤 PROFILE PAGE
# ==============================
@login_required
def Profile(request):
    enrollment = cache.get(f"enrollment_{request.user.id}")
    if enrollment is None:
        enrollment = Enrollment.objects.filter(user=request.user).first()
        cache.set(f"enrollment_{request.user.id}", enrollment, timeout=300)

    image_url = None
    if enrollment and enrollment.face_image:
        image_url = cache.get(f"profile_image_{request.user.id}")
        if image_url is None:
            image_url, _ = cloudinary_url(
                enrollment.face_image.public_id,
                width=130,
                height=130,
                crop="fill",
            )
            cache.set(f"profile_image_{request.user.id}",
                      image_url, timeout=300)

    return render(request, 'profile.html', {
        'enrollment': enrollment,
        'image_url': image_url,
        'is_expired': enrollment.is_expired if enrollment else False,
        'days_remaining': enrollment.days_remaining if enrollment else 0,
    })


# ==============================
# ATTENDANCE PAGE
# ==============================
@login_required  # ✅ Fixed: was missing login_required
def attendence(request):
    today = timezone.localdate()
    user = request.user

    already_mark = Attendence.objects.filter(user=user, date=today).exists()

    if request.method == "POST":
        obj, created = Attendence.objects.get_or_create(user=user, date=today)

        if created:
            messages.success(request, "Attendance successfully marked.")
        else:
            messages.error(request, "Attendance already marked today.")

        return redirect('/attendence/')

    all_attended = list(Attendence.objects.filter(user=user).order_by('-date'))
    attended = all_attended[:7]
    total_days = len(all_attended)
    monthly_days = calendar.monthrange(today.year, today.month)[1]

    return render(request, 'attendence.html', {
        'already_mark': already_mark,
        'attended': attended,
        'total_days': total_days,
        'monthly_days': monthly_days,
        'today': today,
    })
