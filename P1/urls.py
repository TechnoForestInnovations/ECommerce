"""
URL configuration for P1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path("admin/", admin.site.urls),
    path("", views.product_list, name="product_list"),
    path("products/", views.product_list, name="product_list_all"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("remove/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("buy-now/", views.buy_now_form, name="buy_now_form"),
    path("create-order/", views.create_order, name="create_order"),
    # path("payment/success/", views.payment_success, name="payment_success"),
    path("review-order/", views.review_order, name="review_order"),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)