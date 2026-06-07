# ============================================================
#  AuthFit/context_processors.py  (create this new file)
#
#  Injects gym coords + already_marked into every template
#  so base.html can always render window.GYM_CONFIG correctly
#  without each view needing to pass them manually.
#
#  Register in settings.py → TEMPLATES[0]['OPTIONS']['context_processors']:
#    'AuthFit.context_processors.gym_config',
# ============================================================

from django.conf import settings
from django.utils import timezone
from AuthFit.models import Attendence


def gym_config(request):
    """
    Adds gym location config and today's attendance status
    to every template context.
    """
    already_marked = False

    if request.user.is_authenticated:
        today = timezone.localdate()
        already_marked = Attendence.objects.filter(
            user=request.user,
            date=today,
        ).exists()

    return {
        'GYM_LATITUDE':      getattr(settings, 'GYM_LATITUDE',      21.1938),
        'GYM_LONGITUDE':     getattr(settings, 'GYM_LONGITUDE',      81.3509),
        'GYM_RADIUS_METERS': getattr(settings, 'GYM_RADIUS_METERS',  100),
        'already_marked':    already_marked,
    }