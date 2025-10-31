# Import the path function to define URL routes
from django.urls import path

# Import all the view functions from views.py
from . import views

# Define the URL patterns (routes) for this app
urlpatterns = [
    # -------------------------------
    # Home / Landing
    # -------------------------------
    path("", views.home, name="home"),
    path("", views.landing, name="landing"),

    # -------------------------------
    # Authentication
    # -------------------------------
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("login/options/", views.login_options, name="login_options"),
    path("logout/", views.logout_page, name="logout"),

    # -------------------------------
    # Forgot Password
    # -------------------------------
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/reset/", views.forgot_password_reset, name="forgot_password_reset"),

    path("shop_by_season/", views.shop_by_season, name="shop_by_season"),
    path("high_vibes/", views.high_vibes, name="high_vibes"),
    path("low_vibes/", views.low_vibes, name="low_vibes"),
    path("accessories/", views.accessories, name="accessories"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("cart/", views.cart, name="cart"),
    path("update-cart/<int:item_id>/", views.update_cart, name="update_cart"),
    path("signup/", views.signup, name="signup"),
    path("shop_now/", views.shop_now, name="shop_now"),
]
