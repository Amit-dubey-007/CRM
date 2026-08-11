from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name="accounts"

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('register/',views.register,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('verify-otp/',views.verify_otp,name='verify_otp'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('verify-reset-otp/',views.verify_reset_otp,name='verify_reset_otp'),
    path('reset-password/',views.reset_password,name='reset_password'),
    path('resend-register-otp/',views.resend_register_otp,name='resend_register_otp'),
    path('resend-reset-otp/',views.resend_reset_otp,name='resend_reset_otp'),
] 