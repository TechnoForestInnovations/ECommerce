from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('login/', auth_views.LoginView.as_view(template_name='base/login.html'), name='login'),
     path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="logged_out", http_method_names=["get", "post"]),
        name="logout",
    ),
]
