from django.urls import path
from AuthFit import views

urlpatterns = [
    path('',views.homePage , name = "home"),
    path('login/',views.loginPage, name = "loginPage"),
    path('signup/',views.signupPage , name = "signPage"),
    path('workout/',views.workout , name = "workout"), 
    path('profile/',views.Profile , name = "Profile"),
    path('logout/',views.handlelogout , name = "logout"),
    path('contact/',views.contact , name = "contact"),
    path('enrollment/',views.enrollment , name = "enrollment"),
    path('attendence/',views.attendence , name = "attendence"),
    path('api/mark-attendance/', views.mark_attendance_api),
    path('api/get-users/', views.get_users),
    path('api/save-embedding/', views.save_embedding),
    path('api/upload-face-image/', views.upload_face_image),
    path('api/stats/', views.stats_api, name='stats_api'),
]
