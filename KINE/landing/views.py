from django.shortcuts import render, redirect
from django.contrib import auth
# shop/views.py
from django.http import JsonResponse
from .models import Category

def get_enabled_categories(request):
    categories = Category.objects.filter(is_enabled=True)
    data = [
        {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "images": category.image_urls,
            "link": category.link
        }
        for category in categories
    ]
    return JsonResponse({"categories": data})

# -------------------------------
# Home / Landing
# -------------------------------
def home(request):
    categories = Category.objects.filter(is_enabled=True).order_by('order')
    return render(request, 'landing/landing.html', {'categories': categories})

def landing(request):
    categories = Category.objects.filter(is_enabled=True).order_by('order')
    return render(request, "registration/landing.html", {'categories': categories})


def logout_page(request):
    auth.logout(request)
    return redirect("home")
