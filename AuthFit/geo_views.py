# ============================================================
#  Add this view to AuthFit/views.py
#  It's called by the Service Worker automatically when the
#  user walks into the gym (phone in pocket).
#
#  Security model:
#   - credentials: 'include' in SW fetch → Django session cookie
#     is sent, so request.user is the real logged-in user.
#   - No CSRF needed because it's a same-origin credentialed
#     fetch, and we validate the session server-side.
#   - We double-check user_id matches session to prevent
#     any crafted requests from marking another user.
# ============================================================

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from AuthFit.models import Attendence


@csrf_exempt                    # SW can't send CSRF token; session auth is enough
@login_required                 # Must be logged in (session cookie)
def geo_mark_attendance(request):
    """
    POST /api/geo-mark-attendance/
    Called by the Service Worker when the user enters the gym radius.
    Body: { "user_id": <int> }   (used only as a sanity cross-check)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
 
    try:
        data     = json.loads(request.body)
        user_id  = int(data.get('user_id', 0))
 
        # Sanity check: SW user_id must match the session user
        if user_id and user_id != request.user.id:
            return JsonResponse({'error': 'User mismatch'}, status=403)
 
        today = timezone.localdate()
        _, created = Attendence.objects.get_or_create(
            user=request.user,
            date=today,
        )
 
        if created:
            return JsonResponse({'status': 'success',  'message': 'Attendance marked automatically'})
        else:
            return JsonResponse({'status': 'exists',   'message': 'Already marked today'})
 
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
 
# ============================================================
#  Also add this tiny view that serves sw.js from the correct
#  scope (/sw.js) regardless of your STATIC_URL prefix.
#  Without this, the SW scope would be /static/ and it
#  couldn't intercept requests at the root.
# ============================================================
 
import os
from django.http import HttpResponse
from django.conf import settings
 
 
def serve_sw(request):
    """Serve the Service Worker from the root scope /sw.js"""
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
        return HttpResponse('// sw.js not found', content_type='application/javascript', status=404)
 
 
# ============================================================
#  Add this new view to geo_views.py
#  Also add to urls.py:
#  path('api/attendance-status/', attendance_status),
# ============================================================
 
@login_required
def attendance_status(request):
    """
    GET /api/attendance-status/
    Returns whether the current user has already marked
    attendance today. Called by the Service Worker before
    auto-marking to avoid duplicate attempts.
    """
    today = timezone.localdate()
    marked = Attendence.objects.filter(
        user=request.user,
        date=today,
    ).exists()
    return JsonResponse({'marked': marked})