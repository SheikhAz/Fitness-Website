from django.contrib import admin
from django.db.models import Sum
from .models import Contact, Gallery ,Trainer ,MembershipPlan ,Attendence
from .models import Enrollment


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
    change_list_template = "admin/enrollment_change_list.html"

    def changelist_view(self, request, extra_context=None):
        # Get queryset
        qs = self.get_queryset(request)

        # Filter only monthly plan users
        monthly_qs = qs.filter(
        selectPlan__plan__icontains="month",
        paymentStatus="Done"
        )

        # Calculate total income
        total_income = monthly_qs.aggregate(total=Sum('Amount'))['total'] or 0

        extra_context = extra_context or {}
        extra_context['total_income'] = total_income

        return super().changelist_view(request, extra_context=extra_context)
 
