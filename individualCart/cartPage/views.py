# -------------------------------
# Django Imports
# -------------------------------
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt

# -------------------------------
# Python Imports
# -------------------------------
import json, random, re, time, requests
from decimal import Decimal

# -------------------------------
# Models
# -------------------------------
from .models import Address, CartItem, TaxesAndCharges


# ✅ Helper to safely get tax/delivery settings
def get_tax_settings():
    taxes_and_charges = TaxesAndCharges.objects.first()
    if not taxes_and_charges:
        return {
            "tax": 0,
            "min_amount_for_free_delivery": 9999999,  # fallback high
            "delivery_charges": 0,
        }
    return {
        "tax": taxes_and_charges.tax,
        "min_amount_for_free_delivery": taxes_and_charges.min_amount_for_free_delivery,
        "delivery_charges": taxes_and_charges.delivery_charges,
    }


# ✅ CART PAGE
def cart(request):
    """Render cart page for the current user."""
    settings_data = get_tax_settings()
    tax_percentage = settings_data["tax"]
    min_amount_for_free_delivery = settings_data["min_amount_for_free_delivery"]
    delivery_charges = settings_data["delivery_charges"]

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        addresses = Address.objects.filter(user=request.user)
    else:
        cart_items = []
        addresses = None

    # Calculate totals
    total_items = 0
    all_items_eligible_for_cod = True
    for item in cart_items:
        item.subtotal = item.price * item.quantity
        total_items += item.quantity
        if not item.is_available_for_cod:
            all_items_eligible_for_cod = False

    total_price = sum(item.price * item.quantity for item in cart_items)
    delivery_charge = 0 if total_price >= min_amount_for_free_delivery else delivery_charges
    taxes = (tax_percentage / 100) * total_price
    grand_total = total_price + taxes + delivery_charge

    # ✅ Determine default address
    default_address = None
    if addresses:
        default_address = addresses.filter(is_default=True).first() or addresses.first()

    return render(request, "pages/cart.html", {
        "cart_items": cart_items,
        "total_items": total_items,
        "total_price": total_price,
        "addresses": addresses,
        "default_address": default_address,
        "all_items_eligible_for_cod": all_items_eligible_for_cod,
        "taxes": taxes,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
        "min_amount_for_free_delivery": min_amount_for_free_delivery,
        "taxes_and_charges": settings_data,
    })


# ✅ CHECKOUT VIEW
def checkout_view(request):
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first() or addresses.first()

    # Serialize for frontend JS if needed
    addresses_json = json.dumps(list(addresses.values(
        "id", "full_name", "address_line1", "address_line2",
        "city", "state", "pincode", "country",
        "mobile_number", "is_default"
    )), cls=DjangoJSONEncoder)

    return render(request, "checkout.html", {
        "addresses": addresses,
        "default_address": default_address,
        "addresses_json": addresses_json,
    })


# ✅ AJAX CART ITEM UPDATE
def update_cart(request, item_id):
    """AJAX handler to increase/decrease cart item quantity for the logged-in user."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=403)

    try:
        data = json.loads(request.body)
        action = data.get("action")
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease":
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
                return _cart_summary_response(request.user, removed=True)
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)

        cart_item.save()
        return _cart_summary_response(request.user, updated_item=cart_item)

    except CartItem.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ HELPER: Recalculate and format cart summary
def _cart_summary_response(user, updated_item=None, removed=False):
    settings_data = get_tax_settings()
    tax_percentage = settings_data["tax"]
    min_amount_for_free_delivery = settings_data["min_amount_for_free_delivery"]
    delivery_charges = settings_data["delivery_charges"]

    cart_items = CartItem.objects.filter(user=user)
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.price * item.quantity for item in cart_items)
    taxes = (tax_percentage / 100) * total_price
    delivery_charge = 0 if total_price >= min_amount_for_free_delivery else delivery_charges
    grand_total = total_price + taxes + delivery_charge
    all_items_eligible_for_cod = all(item.is_available_for_cod for item in cart_items)

    response = {
        "removed": removed,
        "cart_summary": {
            "total_items": total_items,
            "total_price": f"₹{total_price:.2f}",
            "taxes": f"₹{taxes:.2f}",
            "grand_total": f"₹{grand_total:.2f}",
        },
        "all_items_eligible_for_cod": all_items_eligible_for_cod,
    }

    if updated_item:
        response.update({
            "quantity": updated_item.quantity,
            "subtotal": f"{updated_item.price * updated_item.quantity:.2f}",
        })

    return JsonResponse(response)
