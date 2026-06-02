from django.contrib import admin
from .models import Product, Order ,ProductFlavor

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductFlavor)
admin.site.register(Order)