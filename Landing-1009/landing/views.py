from django.shortcuts import render, redirect
from django.contrib import auth

# -------------------------------
# Home / Landing
# -------------------------------
def home(request):
    return render(request, 'landing/landing.html')

def landing(request):
    return render(request, "registration/landing.html")

# -------------------------------
# Pages
# -------------------------------
def shop_by_season(request):
    return render(request, 'pages/shopbyseason.html')

def high_vibes(request):
    return render(request, 'pages/highvibes.html')

def low_vibes(request):
    return render(request, 'pages/lowvibes.html')

def accessories(request):
    return render(request, 'pages/accessories.html')

def wishlist(request):
    return render(request, 'pages/wishlist.html')

def shop_now(request):
    return render(request, 'pages/shopnow.html')

def cart(request):
    return render(request, 'pages/cart.html')
def logout_page(request):
    auth.logout(request)
    return redirect("home")
def login_page(request):
    return render(request, 'pages/login.html')
def signup_page(request):
    return render(request, 'pages/signup.html')
