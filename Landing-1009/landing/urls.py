from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------
    # Home / Landing
    # -------------------------------
    path("", views.home, name="home"),
    path("landing/", views.landing, name="landing"),

    # -------------------------------
    # Pages
    # -------------------------------
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("shop_by_season/", views.shop_by_season, name="shop_by_season"),
    path("high_vibes/", views.high_vibes, name="high_vibes"),
    path("low_vibes/", views.low_vibes, name="low_vibes"),
    path("accessories/", views.accessories, name="accessories"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("cart/", views.cart, name="cart"),
    path("shop_now/", views.shop_now, name="shop_now"),
    path("logout/", views.logout_page, name="logout"),
]
