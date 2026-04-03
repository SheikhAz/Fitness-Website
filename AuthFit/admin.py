from django.contrib import admin
from .models import Contact,Trainer ,MembershipPlan ,Attendence
from .models import Enrollment
from django.urls import path
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.template.response import TemplateResponse
import json


def revenue_view(request):
    qs = Enrollment.objects.filter(paymentStatus="Done")

    # 📊 Monthly Revenue
    monthly = (
        qs.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('Amount'))
        .order_by('month')
    )

    # 📅 Daily Revenue (last 7 days)
    last_7_days = timezone.now() - timezone.timedelta(days=7)

    daily = (
        qs.filter(created_at__gte=last_7_days)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total=Sum('Amount'))
        .order_by('day')
    )

    # 📈 Member Growth
    members = (
        Enrollment.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # 💳 Payment Analytics
    payments = (
        Enrollment.objects
        .exclude(paymentStatus__isnull=True)
        .values('paymentStatus')
        .annotate(count=Count('id'))
    )

    # ✅ KPI CALCULATIONS (IMPORTANT)
    total_revenue = sum([x['total'] or 0 for x in monthly])
    today_revenue = sum([x['total'] or 0 for x in daily])
    total_members = Enrollment.objects.count()

    context = dict(
        admin.site.each_context(request),

        # Charts
        monthly_labels=json.dumps([x['month'].strftime("%b %Y")
                                  for x in monthly if x['month']]),
        monthly_data=json.dumps([float(x['total'] or 0) for x in monthly]),

        daily_labels=json.dumps([x['day'].strftime("%d %b")
                                for x in daily if x['day']]),
        daily_data=json.dumps([float(x['total'] or 0) for x in daily]),

        member_labels=json.dumps([x['month'].strftime("%b %Y")
                                 for x in members if x['month']]),
        member_data=json.dumps([x['count'] for x in members]),

        payment_labels=json.dumps([x['paymentStatus'] for x in payments]),
        payment_data=json.dumps([x['count'] for x in payments]),

        # ✅ REAL VALUES (for KPI cards)
        total_revenue=total_revenue,
        today_revenue=today_revenue,
        total_members=total_members,
    )

    return TemplateResponse(request, "admin/revenue.html", context)


original_get_urls = admin.site.get_urls


def custom_get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('revenue/', admin.site.admin_view(revenue_view)),
    ]
    return custom_urls + urls


admin.site.get_urls = custom_get_urls

# Register your models here.
admin.site.register(Contact)
admin.site.register(Trainer)
admin.site.register(MembershipPlan)

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
    list_display = (
        "unique_id",
        "fullname",
        "phone",
        "selectPlan",
        "paymentStatus",
        "days_remaining",
        "face_preview",  
    )

    search_fields = ("unique_id", "fullname", "phone", "email")

    list_filter = ("paymentStatus", "selectPlan", "trainer", "gender")

    readonly_fields = ("face_preview",)  # ✅ show in detail page

    # ✅ IMAGE PREVIEW FUNCTION
    def face_preview(self, obj):
        if obj.face_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%; object-fit:cover;" />',
                obj.face_image.url
            )
        return "No Image"

    face_preview.short_description = "Face"
