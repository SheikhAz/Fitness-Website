# shop/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('products/',views.product_list,   name='product_list'),
    path('product/<int:product_id>/',views.product_detail, name='product_detail'),

    path('product/<int:product_id>/confirm/', views.confirm_order,  name='confirm_order'),

    path('order/place/', views.place_order,    name='place_order'),

    path('orders/',views.my_orders,      name='my_orders'),

    path('manage/orders/',views.order_dashboard, name='admin_orders'),
    path('manage/orders/<int:order_id>/update/', views.order_update,    name='admin_order_update'),
]