import random, re, time, requests

from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

# OTP storage
otp_storage = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    send_mail(
        'Your OTP',
        f'Your OTP is: {otp}',
        'sreeja.bommana1123@gmail.com',
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

# ===================== SIGNUP =====================
def signup(request):
    context = {"errors": {}, "otp_section": False, "resend_disabled": True}

    # STEP 1: Register
    if request.method == "POST" and "register" in request.POST:
        fname = request.POST.get("full_name")
        contact = request.POST.get("contact")   # Email OR mobile
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

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

        if errors:
            context["errors"] = errors
            return render(request, "registration/signup.html", context)

        # Generate OTP
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

    # STEP 2: Verify OTP
    if request.method == "POST" and "verify" in request.POST:
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
            return redirect("landing_view")
        else:
            context["errors"]["otp"] = "Invalid OTP"
            context["otp_section"] = True
            context["contact"] = contact
            return render(request, "registration/signup.html", context)

    # STEP 3: Resend
    if request.method == "POST" and "resend" in request.POST:
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

    return render(request, "registration/signup.html", context)

def landing(request):
    return render(request, "registration/landing.html")

# ------------------ LOGIN ------------------
def login_view(request):
    if request.method == "POST":
        email_or_mobile = request.POST.get("email_or_mobile")
        password = request.POST.get("password")

        try:
            if "@" in email_or_mobile:
                user_obj = User.objects.filter(email=email_or_mobile).first()
            else:
                user_obj = User.objects.filter(username=email_or_mobile).first()
        except User.DoesNotExist:
            user_obj = None

        if not user_obj:
            messages.error(request, "Invalid Email/Mobile or Password")
            return redirect("login")

        user = authenticate(username=user_obj.username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("landing_view")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")

    return render(request, "registration/login.html")

# ------------------ FORGOT PASSWORD ------------------
# ------------------ FORGOT PASSWORD ------------------
def forgot_password(request):
    context = {"errors": {}, "otp_section": False, "contact": None, "resend_disabled": True}

    # STEP 1: Enter Email/Mobile → Send OTP
    if request.method == "POST" and "send_otp" in request.POST:
        contact = request.POST.get("email_or_mobile")

        # Check if user exists
        if "@" in contact:
            user = User.objects.filter(email=contact).first()
        else:
            user = User.objects.filter(username=contact).first()

        if not user:
            context["errors"]["contact"] = "User not found with this Email/Mobile"
            return render(request, "registration/forgot_password.html", context)

        # Generate OTP and save
        otp = generate_otp()
        otp_storage[contact] = {
            "otp": otp,
            "timestamp": time.time(),
        }

        # Send OTP
        if "@" in contact:
            send_otp_email(contact, otp)
        else:
            send_otp_sms(contact, otp)

        context["otp_section"] = True
        context["contact"] = contact
        messages.success(request, "OTP has been sent")
        return render(request, "registration/forgot_password.html", context)

    # STEP 2: Verify OTP
    if request.method == "POST" and "verify" in request.POST:
        contact = request.POST.get("contact")   # hidden field lo store
        entered_otp = request.POST.get("otp")

        otp_data = otp_storage.get(contact)
        if not otp_data:
            context["errors"]["otp"] = "No OTP generated. Please resend."
            context["otp_section"] = True
            context["contact"] = contact
            return render(request, "registration/forgot_password.html", context)

        # Expiry check (5 min)
        if time.time() - otp_data["timestamp"] > 300:
            context["errors"]["otp"] = "OTP expired. Please resend."
            context["otp_section"] = True
            context["contact"] = contact
            context["resend_disabled"] = False
            return render(request, "registration/forgot_password.html", context)

        if entered_otp == otp_data["otp"]:
            # Save in session to allow reset
            request.session["reset_user"] = contact
            return redirect("forgot_password_reset")
        else:
            context["otp_section"] = True
            context["contact"] = contact
            context["errors"]["otp"] = "Invalid OTP"
            return render(request, "registration/forgot_password.html", context)

    # STEP 3: Resend OTP
    if request.method == "POST" and "resend" in request.POST:
        contact = request.POST.get("contact")

        # If OTP already generated → check 60 sec restriction
        if contact in otp_storage and time.time() - otp_storage[contact]["timestamp"] < 60:
            wait = int(60 - (time.time() - otp_storage[contact]["timestamp"]))
            context["otp_section"] = True
            context["contact"] = contact
            messages.error(request, f"Please wait {wait} seconds before resending OTP")
            return render(request, "registration/forgot_password.html", context)

        # Always generate new OTP on Resend
        otp = generate_otp()
        otp_storage[contact] = {"otp": otp, "timestamp": time.time()}

        if "@" in contact:
            send_otp_email(contact, otp)
        else:
            send_otp_sms(contact, otp)

        context["otp_section"] = True
        context["contact"] = contact
        context["resend_disabled"] = True  # disable button for 60 sec
        messages.success(request, "OTP resent successfully")
        return render(request, "registration/forgot_password.html", context)

    return render(request, "registration/forgot_password.html", context)


# ------------------ RESET PASSWORD ------------------
def forgot_password_reset(request):
    user_key = request.session.get("reset_user")
    if not user_key:
        return redirect("forgot_password")

    context = {"errors": {}}

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate password
        if not is_valid_password(new_password):
            context["errors"]["password"] = "Password must be 8+ chars with uppercase, lowercase, number & special character"

        if new_password != confirm_password:
            context["errors"]["confirm_password"] = "Passwords do not match"

        if context["errors"]:
            return render(request, "registration/forgot_password_reset.html", context)

        # Get user
        if "@" in user_key:
            user = User.objects.filter(email=user_key).first()
        else:
            user = User.objects.filter(username=user_key).first()

        if user:
            user.set_password(new_password)
            user.save()

        # Clear OTP and session
        otp_storage.pop(user_key, None)
        request.session.pop("reset_user", None)

        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "registration/forgot_password_reset.html", context)
