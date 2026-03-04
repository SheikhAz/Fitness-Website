from django.contrib import admin
from .models import Contact, Gallery ,Trainer ,MembershipPlan ,Attendence
from .models import Enrollment
from django.utils import timezone


# Register your models here.
admin.site.register(Contact)
admin.site.register(Trainer)
admin.site.register(MembershipPlan)
admin.site.register(Gallery)


@admin.register(Attendence)
class AttendenceAdmin(admin.ModelAdmin):

    list_display = ('member_id', 'member_name', 'date', 'timestamp')
    search_fields = ('user__enrollment__fullname',
                     'user__enrollment__unique_id')
    list_filter = ('date',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        today = timezone.localdate()
        return qs.filter(date=today)

    def member_id(self, obj):
        return obj.user.enrollment.unique_id
    member_id.short_description = "MEMBER ID"

    def member_name(self, obj):
        return obj.user.enrollment.fullname
    member_name.short_description = "NAME"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "fullname", "phone",
                    "selectPlan", "paymentStatus", "days_remaining")
    search_fields = ("unique_id", "fullname", "phone", "email")
    list_filter = ("paymentStatus", "selectPlan", "trainer", "gender")
