from django.urls import path
from . import views

app_name = "base"

urlpatterns = [
    # Signup + Landing
    path("signup/", views.signup, name="signup"),
    path("landing/", views.landing, name="landing"),

    # Login
    path("login/", views.login_view, name="login"),

    # Forgot Password Flow
    path("forgot-password/", views.forgot_password, name="forgot_password"),
   
    path("forgot-password/reset/", views.forgot_password_reset, name="forgot_password_reset"),
]
