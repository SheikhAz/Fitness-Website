from django.urls import path
from AuthFit import views

urlpatterns = [
    path('',views.homePage , name = "home"),
    path('login/',views.loginPage, name = "loginPage"),
    path('signup/',views.signupPage , name = "signPage"),
    path('workout/',views.workout , name = "workout"), 
    path('profile/',views.Profile , name = "Profile"),
    path('logout/',views.handlelogout , name = "logout"),
]
