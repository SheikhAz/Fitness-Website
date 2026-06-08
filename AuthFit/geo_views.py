import os
import json
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from AuthFit.models import Attendence, Enrollment


@csrf_exempt
@login_required
def geo_mark_attendance(request):
    """
    POST /api/geo-mark-attendance/
    Called by the Service Worker when the user enters the gym radius.
    Only marks attendance for enrolled members.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data    = json.loads(request.body)
        user_id = int(data.get('user_id', 0))

        # Sanity check: SW user_id must match the session user
        if user_id and user_id != request.user.id:
            return JsonResponse({'error': 'User mismatch'}, status=403)

        # ── NEW: Only enrolled members can mark attendance ──────
        try:
            enrollment = Enrollment.objects.get(user=request.user)
        except Enrollment.DoesNotExist:
            return JsonResponse({
                'status': 'not_enrolled',
                'message': 'You are not enrolled yet. Please enroll to mark attendance.'
            }, status=403)

        # ── Optional: block expired memberships ─────────────────
        if enrollment.is_expired:
            return JsonResponse({
                'status': 'expired',
                'message': 'Your membership has expired. Please renew to mark attendance.'
            }, status=403)

        # ── Mark attendance ──────────────────────────────────────
        today = timezone.localdate()
        _, created = Attendence.objects.get_or_create(
            user=request.user,
            date=today,
        )

        if created:
            return JsonResponse({
                'status': 'success',
                'message': 'Attendance marked automatically'
            })
        else:
            return JsonResponse({
                'status': 'exists',
                'message': 'Already marked today'
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def attendance_status(request):
    """
    GET /api/attendance-status/
    Returns whether the current enrolled user has marked attendance today.
    If not enrolled, returns marked: false so SW doesn't try to auto-mark.
    """
    # ── Not enrolled → tell SW to not bother trying ─────────────
    is_enrolled = Enrollment.objects.filter(user=request.user).exists()
    if not is_enrolled:
        return JsonResponse({'marked': False, 'enrolled': False})

    today  = timezone.localdate()
    marked = Attendence.objects.filter(
        user=request.user,
        date=today,
    ).exists()

    return JsonResponse({'marked': marked, 'enrolled': True})


def serve_sw(request):
    """Serve the Service Worker from root scope /sw.js"""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
        return HttpResponse(
            content,
            content_type='application/javascript',
            headers={
                'Service-Worker-Allowed': '/',
                'Cache-Control': 'no-cache',
            }
        )
    except FileNotFoundError:
        return HttpResponse(
            '// sw.js not found',
            content_type='application/javascript',
            status=404
        )