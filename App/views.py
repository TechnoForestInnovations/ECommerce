from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from .models import Product,Wishlist,ProductSize
from django.contrib.auth.decorators import login_required
def product_list(request):
    products = Product.objects.all()
    # Sorting
    sort = request.GET.get('sort')
    if sort == "price":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")

    # Filtering by season
    season = request.GET.get('season')
    if season:
        products = products.filter(season=season)
    return render(request, "App/product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, "App/product_detail.html", {
        "product": product,
        "in_wishlist": in_wishlist
    })



def wishlist_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("product")

    return render(request, "App/wishlist.html", {"wishlist_items": wishlist_items})

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect("wishlist")

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:  # already exists → remove it
        wishlist_item.delete()
        in_wishlist = False
    else:
        in_wishlist = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"in_wishlist": in_wishlist})
    return redirect("product_detail", pk=product.id)


#

# shop/views.py
import json
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponse


# instantiate razorpay client once
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def buy_now_form(request):
    """
    Example product page with a 'Buy Now' form for demonstration.
    In real app you'd pass product details and price dynamically.
    """
    # Example product info:
    product = {
        "id": 101,
        "name": "Sample Product",
        "price_rupees": 499  # ₹499
    }
    return render(request, "App/product_detail.html", {"product": product})


@transaction.atomic
def create_order(request):
    """
    Called when user clicks 'Buy Now'. Creates Order in DB and
    Razorpay Order (server-side), then renders checkout template.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    # In real app take these from form / logged-in user
    full_name = request.POST.get("full_name") or "Guest User"
    email = request.POST.get("email") or "guest@example.com"
    phone = request.POST.get("phone") or ""
    price_rupees = int(request.POST.get("price_rupees") or 499)  # rupees
    amount_paise = price_rupees * 100

    # Create local Order
    order = Order.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        amount=amount_paise,
        status='created'
    )

    # Create Razorpay order
    DATA = {
        "amount": amount_paise,  # amount in paise
        "currency": "INR",
        "receipt": f"order_rcpt_{order.id}",
        "notes": {
            "order_id": str(order.id),
            "customer_name": full_name
        }
    }
    razorpay_order = razorpay_client.order.create(data=DATA)

    # save razorpay order id to our order
    order.razorpay_order_id = razorpay_order.get("id")
    order.save()

    # pass necessary details to template with checkout.js
    context = {
        "order": order,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order.get("id"),
        "amount": amount_paise,
        "currency": "INR",
        "callback_url": request.build_absolute_uri("/payment/success/")  # adjust path if needed
    }
    return render(request, "App/payment.html", context)

#
# @csrf_exempt
# @transaction.atomic
# def payment_success(request):
#     """
#     Endpoint that receives the POST from the checkout form after payment.
#     We verify signature server-side using Razorpay client utility.
#     """
#     if request.method != "POST":
#         return HttpResponseBadRequest("Invalid request method")
#
#     payload = request.POST
#     # Required fields from Razorpay checkout
#     razorpay_payment_id = payload.get("razorpay_payment_id")
#     razorpay_order_id = payload.get("razorpay_order_id")
#     razorpay_signature = payload.get("razorpay_signature")
#
#     if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
#         return HttpResponseBadRequest("Missing payment parameters")
#
#     # Find matching Order
#     try:
#         order = Order.objects.get(razorpay_order_id=razorpay_order_id)
#     except Order.DoesNotExist:
#         return HttpResponseBadRequest("Order not found")
#
#     # Verify signature
#     params_dict = {
#         'razorpay_order_id': razorpay_order_id,
#         'razorpay_payment_id': razorpay_payment_id,
#         'razorpay_signature': razorpay_signature
#     }
#
#     try:
#         razorpay_client.utility.verify_payment_signature(params_dict)
#     except razorpay.errors.SignatureVerificationError:
#         # Signature mismatch -> payment is not verified
#         order.status = 'failed'
#         order.save()
#         return render(request, "App/failed.html", {"order": order, "reason": "Signature verification failed"})
#
#     # Signature verified. Save Payment record and mark order paid
#     # Optionally fetch payment details from Razorpay for more info
#     try:
#         payment_details = razorpay_client.payment.fetch(razorpay_payment_id)
#     except Exception:
#         payment_details = {}
#
#     Payment.objects.create(
#         order=order,
#         razorpay_payment_id=razorpay_payment_id,
#         razorpay_order_id=razorpay_order_id,
#         razorpay_signature=razorpay_signature,
#         amount=order.amount,
#         raw_response=payment_details
#     )
#
#     order.status = 'paid'
#     order.save()
#
#     # Optionally: generate invoice, send email, reduce stock etc.
#     return render(request, "App/success.html", {"order": order, "payment": payment_details})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, ProductSize

def review_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        selected_size = request.POST.get('size')

        if not product_id:
            messages.error(request, "No product selected.")
            return redirect('product_list')

        if not selected_size:
            messages.error(request, "Please select a size.")
            return redirect('product_detail', pk=product_id)

        product = get_object_or_404(Product, id=product_id)

        # Get ProductSize object
        product_size = get_object_or_404(ProductSize, product=product, size=selected_size)

        if product_size.stock <= 0:
            messages.error(request, f"Size {product_size.size} is out of stock.")
            return redirect('product_detail', pk=product_id)

        context = {
            'product': product,
            'product_size': product_size,
            'images': product.images.all(),
        }
        return render(request, 'App/review_order.html', context)

    messages.warning(request, "Invalid request method.")
    return redirect('product_list')
