from django.contrib import admin
from .models import Contact ,Trainer 
from .models import Enrollment
# Register your models here.
admin.site.register(Contact)
admin.site.register(Enrollment)
admin.site.register(Trainer)