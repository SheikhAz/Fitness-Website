from django.contrib import admin
from .models import Contact, Gallery ,Trainer ,MembershipPlan
from .models import Enrollment
# Register your models here.
admin.site.register(Contact)
admin.site.register(Trainer)
admin.site.register(MembershipPlan)
admin.site.register(Gallery)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "fullname", "phone",
                    "selectPlan", "paymentStatus", "days_remaining")
    search_fields = ("unique_id", "fullname", "phone", "email")
    list_filter = ("paymentStatus", "selectPlan", "trainer", "gender")
    ordering = ("-id",)
