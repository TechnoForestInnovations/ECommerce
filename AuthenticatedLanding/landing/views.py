# -------------------------------
# Django Imports
# -------------------------------
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login

# -------------------------------
# Python Imports
# -------------------------------
import json, random, re, time, requests
from decimal import Decimal

# -------------------------------
# Models
# -------------------------------
from .models import Subscriber, CartItem


# -------------------------------
# Templates / Constants
# -------------------------------
FORGOT_PASSWORD_TEMPLATE = "registration/forgot_password.html"
LOGIN_TEMPLATE = "registration/login.html"
INVALID_OTP_MESSAGE = "Invalid OTP"

# OTP storage (temporary, in-memory)
otp_storage = {}

# -------------------------------
# Helper Functions
# -------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    send_mail(
        'Your OTP',
        f'Your OTP is: {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_otp_sms(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "sender_id": "TXTIND",
        "message": f"Your OTP is {otp}",
        "language": "english",
        "route": "q",
        "numbers": mobile
    }
    headers = {
        "authorization": settings.FAST2SMS_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        print("Fast2SMS Response:", response.json())
    except Exception as e:
        print("SMS Error:", e)


def is_valid_password(password):
    return re.match(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        password
    )


def is_valid_name(name):
    return re.match(r'^[A-Za-z ]+$', name)


# -------------------------------
# Home / Landing
# -------------------------------
def home(request):
    return render(request, 'landing/index.html')


def landing(request):
    return render(request, "registration/landing.html")


# -------------------------------
# SIGNUP
# -------------------------------
def signup(request):
    context = {"errors": {}, "otp_section": False, "resend_disabled": True}

    if request.method == "POST":
        if "register" in request.POST:
            return _signup_register(request, context)
        elif "verify" in request.POST:
            return _signup_verify(request, context)
        elif "resend" in request.POST:
            return _signup_resend(request, context)

    return render(request, "registration/signup.html", context)


def _signup_register(request, context):
    fname = request.POST.get("full_name")
    contact = request.POST.get("contact")
    password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")

    errors = _validate_signup_form(fname, contact, password, confirm_password)
    if errors:
        context["errors"] = errors
        return render(request, "registration/signup.html", context)

    is_email = re.match(r"[^@]+@[^@]+\.[^@]+", contact)
    is_mobile = re.match(r'^[6-9]\d{9}$', contact)

    otp = generate_otp()
    otp_storage[contact] = {
        "otp": otp,
        "timestamp": time.time(),
        "data": {
            "full_name": fname,
            "contact": contact,
            "password": password,
            "is_email": bool(is_email),
            "is_mobile": bool(is_mobile)
        }
    }

    if is_email:
        send_otp_email(contact, otp)
    elif is_mobile:
        send_otp_sms(contact, otp)

    context["otp_section"] = True
    context["contact"] = contact
    return render(request, "registration/signup.html", context)


def _signup_verify(request, context):
    contact = request.POST.get("contact")
    entered_otp = request.POST.get("otp")

    if contact not in otp_storage:
        context["errors"]["otp"] = "No OTP generated for this user."
        return render(request, "registration/signup.html", context)

    otp_data = otp_storage[contact]

    if time.time() - otp_data["timestamp"] > 300:
        context["errors"]["otp"] = "OTP expired. Please resend."
        context["otp_section"] = True
        context["contact"] = contact
        context["resend_disabled"] = False
        return render(request, "registration/signup.html", context)

    if entered_otp == otp_data["otp"]:
        User.objects.create_user(
            username=contact,
            first_name=otp_data["data"]["full_name"],
            email=contact if otp_data["data"]["is_email"] else "",
            password=otp_data["data"]["password"]
        )
        del otp_storage[contact]
        return redirect("landing")


def _signup_resend(request, context):
    contact = request.POST.get("contact")
    if contact in otp_storage:
        otp = generate_otp()
        otp_storage[contact]["otp"] = otp
        otp_storage[contact]["timestamp"] = time.time()

        if otp_storage[contact]["data"]["is_email"]:
            send_otp_email(contact, otp)
        else:
            send_otp_sms(contact, otp)

        context["otp_section"] = True
        context["resend_disabled"] = True
        context["contact"] = contact
    return render(request, "registration/signup.html", context)


def _validate_signup_form(fname, contact, password, confirm_password):
    errors = {}
    if not is_valid_name(fname):
        errors["full_name"] = "Full name must contain only alphabets"

    is_email = re.match(r"[^@]+@[^@]+\.[^@]+", contact)
    is_mobile = re.match(r'^[6-9]\d{9}$', contact)

    if not is_email and not is_mobile:
        errors["contact"] = "Enter valid Email or Mobile Number"

    if not is_valid_password(password):
        errors["password"] = "Password must be 8+ chars with uppercase, lowercase, number & special character"
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"

    if User.objects.filter(username=contact).exists():
        errors["contact"] = "This user already registered"

    return errors


# -------------------------------
# LOGIN
# -------------------------------
def login_view(request):
    context = {"otp_section": False, "contact": None, "resend_disabled": True, "active_tab": "password"}

    if request.method == "POST":
        if "password_login" in request.POST:
            return _handle_password_login(request, context)
        elif "send_otp" in request.POST:
            return _handle_send_otp(request, context)
        elif "verify" in request.POST:
            return _handle_verify_otp(request, context)

    tab = request.GET.get("tab")
    if tab in ["password", "otp"]:
        context["active_tab"] = tab
    return render(request, LOGIN_TEMPLATE, context)


def _handle_password_login(request, context):
    email_or_mobile = request.POST.get("email_or_mobile")
    password = request.POST.get("password")

    user = User.objects.filter(email=email_or_mobile).first() if "@" in email_or_mobile else User.objects.filter(username=email_or_mobile).first()
    if user and user.check_password(password):
        auth_login(request, user)
        return redirect("landing")
    else:
        messages.error(request, "Invalid credentials")
        context["active_tab"] = "password"
        return render(request, LOGIN_TEMPLATE, context)


def _handle_send_otp(request, context):
    contact = request.POST.get("email_or_mobile")
    user = User.objects.filter(email=contact).first() if "@" in contact else User.objects.filter(username=contact).first()
    if not user:
        messages.error(request, "User not found")
        context["active_tab"] = "otp"
    else:
        otp = generate_otp()
        otp_storage[contact] = {"otp": otp, "timestamp": time.time(), "is_email": "@" in contact}
        if "@" in contact:
            send_otp_email(contact, otp)
        else:
            send_otp_sms(contact, otp)
        context.update({"otp_section": True, "contact": contact, "active_tab": "otp"})
    return render(request, LOGIN_TEMPLATE, context)


def _handle_verify_otp(request, context):
    contact = request.POST.get("contact")
    otp_entered = request.POST.get("otp")
    otp_data = otp_storage.get(contact)
    context.update({"otp_section": True, "contact": contact, "active_tab": "otp"})
    if otp_data and otp_entered == otp_data["otp"]:
        user = User.objects.filter(email=contact).first() if otp_data["is_email"] else User.objects.filter(username=contact).first()
        if user:
            auth_login(request, user)
            del otp_storage[contact]
            return redirect("landing")
        messages.error(request, INVALID_OTP_MESSAGE)
    return render(request, LOGIN_TEMPLATE, context)


def login_options(request):
    return render(request, "login_options.html")


# -------------------------------
# LOGOUT
# -------------------------------
def logout_page(request):
    auth.logout(request)
    return redirect("home")


# -------------------------------
# FORGOT PASSWORD
# -------------------------------
def forgot_password(request):
    context = {"errors": {}, "otp_section": False, "contact": None, "resend_disabled": True}

    if request.method == "POST":
        if "send_otp" in request.POST:
            return _forgot_password_send_otp(request, context)
        elif "verify" in request.POST:
            return _forgot_password_verify_otp(request, context)
        elif "resend" in request.POST:
            return _forgot_password_resend_otp(request, context)

    return render(request, FORGOT_PASSWORD_TEMPLATE, context)


def _forgot_password_send_otp(request, context):
    contact = request.POST.get("email_or_mobile")
    user = User.objects.filter(email=contact).first() if "@" in contact else None
    if not user:
        context["errors"]["contact"] = "User not found with this Email/Mobile"
        return render(request, FORGOT_PASSWORD_TEMPLATE, context)

    otp = generate_otp()
    otp_storage[contact] = {"otp": otp, "timestamp": time.time()}

    send_otp_email(contact, otp)
    context["otp_section"] = True
    context["contact"] = contact
    messages.success(request, "OTP has been sent")
    return render(request, FORGOT_PASSWORD_TEMPLATE, context)


def _forgot_password_verify_otp(request, context):
    contact = request.POST.get("contact")
    entered_otp = request.POST.get("otp")
    otp_data = otp_storage.get(contact)
    if not otp_data:
        return render(request, FORGOT_PASSWORD_TEMPLATE, context)

    if time.time() - otp_data["timestamp"] > 300:
        context["errors"]["otp"] = "OTP expired. Please resend."
        context["otp_section"] = True
        context["contact"] = contact
        context["resend_disabled"] = False
        return render(request, FORGOT_PASSWORD_TEMPLATE, context)

    if entered_otp == otp_data["otp"]:
        request.session["reset_user"] = contact
        return redirect("base:forgot_password_reset")

    context["otp_section"] = True
    context["errors"]["otp"] = INVALID_OTP_MESSAGE
    return render(request, FORGOT_PASSWORD_TEMPLATE, context)


def _forgot_password_resend_otp(request, context):
    contact = request.POST.get("contact")
    otp = generate_otp()
    otp_storage[contact] = {"otp": otp, "timestamp": time.time()}

    send_otp_email(contact, otp)
    context["otp_section"] = True
    context["contact"] = contact
    context["resend_disabled"] = True
    messages.success(request, "OTP resent successfully")
    return render(request, FORGOT_PASSWORD_TEMPLATE, context)


# -------------------------------
# RESET PASSWORD
# -------------------------------
def forgot_password_reset(request):
    user_key = request.session.get("reset_user")
    if not user_key:
        return redirect("base:forgot_password")

    context = {"errors": {}}

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not is_valid_password(new_password):
            context["errors"]["password"] = "Password must be 8+ chars with uppercase, lowercase, number & special character"

        if new_password != confirm_password:
            context["errors"]["confirm_password"] = "Passwords do not match"

        if context["errors"]:
            return render(request, "registration/forgot_password_reset.html", context)

        user = User.objects.filter(email=user_key).first() if "@" in user_key else User.objects.filter(username=user_key).first()

        if user:
            user.set_password(new_password)
            user.save()

        otp_storage.pop(user_key, None)
        request.session.pop("reset_user", None)

        messages.success(request, "Password reset successful. Please login.")
        return redirect("base:login")

    return render(request, "registration/forgot_password_reset.html", context)


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



def cart(request):
    """
    Render cart page for the current user.
    """
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart_items = []  # optionally handle guest session cart here

    # Calculate subtotal for each item
    for item in cart_items:
        item.subtotal = item.price * item.quantity

    # Calculate total items and total price
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.price * item.quantity for item in cart_items)

    return render(request, 'pages/cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price
    })


@csrf_exempt
def update_cart(request, item_id):
    """
    AJAX handler to increase/decrease cart item quantity for the logged-in user.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=403)

    data = json.loads(request.body)
    action = data.get("action")

    try:
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

        if action == "increase":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "decrease":
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
                # Recalculate totals after removal
                cart_items = CartItem.objects.filter(user=request.user)
                total_items = sum(item.quantity for item in cart_items)
                total_price = sum(item.price * item.quantity for item in cart_items)
                return JsonResponse({
                    "removed": True,
                    "cart_summary": {
                        "total_items": total_items,
                        "total_price": f"₹{total_price:.2f}",
                    }
                })
            else:
                cart_item.save()

        # Calculate subtotal for this item
        subtotal = cart_item.price * cart_item.quantity

        # Recalculate totals for the whole cart
        cart_items = CartItem.objects.filter(user=request.user)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.price * item.quantity for item in cart_items)

        return JsonResponse({
            "quantity": cart_item.quantity,
            "subtotal": f"{subtotal:.2f}",
            "removed": False,
            "cart_summary": {
                "total_items": total_items,
                "total_price": f"₹{total_price:.2f}",
            }
        })

    except CartItem.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
def shop_now(request):
    return render(request, 'pages/shopnow.html')