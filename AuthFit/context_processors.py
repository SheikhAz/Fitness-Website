from django.conf import settings
from django.utils import timezone
from AuthFit.models import Attendence, Enrollment


def gym_config(request):
    already_marked = False
    is_enrolled    = False

    if request.user.is_authenticated:
        today = timezone.localdate()

        # Check enrollment
        is_enrolled = Enrollment.objects.filter(user=request.user).exists()

        # Only check attendance if enrolled
        if is_enrolled:
            already_marked = Attendence.objects.filter(
                user=request.user,
                date=today,
            ).exists()

    return {
        'GYM_LATITUDE':      getattr(settings, 'GYM_LATITUDE',      21.1938),
        'GYM_LONGITUDE':     getattr(settings, 'GYM_LONGITUDE',      81.3509),
        'GYM_RADIUS_METERS': getattr(settings, 'GYM_RADIUS_METERS',  100),
        'already_marked':    already_marked,
        'is_enrolled':       is_enrolled,
    }