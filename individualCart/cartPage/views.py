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
from .models import  Address, CartItem,TaxesAndCharges


def cart(request):
    """
    Render cart page for the current user.
    """
    all_items_eligible_for_cod = True
    taxes_and_charges = TaxesAndCharges.objects.first()

    tax_percentage = taxes_and_charges.tax
    min_amount_for_free_delivery = taxes_and_charges.min_amount_for_free_delivery
    delivery_charges = taxes_and_charges.delivery_charges

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        addresses = request.user.addresses.filter(user=request.user)
    else:
        cart_items = []
        addresses = None

    # Calculate totals
    total_items = 0
    for item in cart_items:
        item.subtotal = item.price * item.quantity
        total_items += item.quantity
        if not item.is_available_for_cod:
            all_items_eligible_for_cod = False
    total_price = sum(item.price * item.quantity for item in cart_items)

    if total_price >= min_amount_for_free_delivery:
        delivery_charge = 0
    else:
        delivery_charge = delivery_charges

    taxes = (tax_percentage / 100) * total_price
    grand_total = total_price + taxes + delivery_charge

    return render(request, 'pages/cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
        'addresses': addresses,
        'all_items_eligible_for_cod': all_items_eligible_for_cod,
        'taxes': taxes,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'min_amount_for_free_delivery': min_amount_for_free_delivery,
        'taxes_and_charges': taxes_and_charges,
    })

def checkout_view(request):
    addresses = Address.objects.filter(user=request.user)

    # ✅ Explicitly include all fields needed for frontend display
    addresses_json = json.dumps(list(addresses.values(
        'id',
        'full_name',
        'address_line1',
        'city',
        'state',
        'pincode',
        'country',
        'mobile_number',
        'is_default'
    )), cls=DjangoJSONEncoder)

    return render(request, "checkout.html", {
        "addresses": addresses,
        "addresses_json": addresses_json,
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
                tax_percentage = TaxesAndCharges.objects.first().tax
                min_amount_for_free_delivery=TaxesAndCharges.objects.first().min_amount_for_free_delivery
                all_items_eligible_for_cod = True
                for item in cart_items:
                    if not item.is_available_for_cod:
                        all_items_eligible_for_cod = False
                if total_price >= min_amount_for_free_delivery:
                    delivery_charges=0
                else:
                    delivery_charges=TaxesAndCharges.objects.first().delivery_charges
                taxes = (tax_percentage / 100) * total_price
                grand_total = total_price + taxes + delivery_charges

                return JsonResponse({
                    "removed": True,
                    "cart_summary": {
                        "total_items": total_items,
                        "total_price": f"₹{total_price:.2f}",
                        "taxes": f"₹{taxes:.2f}",
                        "grand_total": f"₹{grand_total:.2f}"
                    },
                    'all_items_eligible_for_cod': all_items_eligible_for_cod,
                })
            else:
                cart_item.save()

        # Calculate subtotal for this item
        subtotal = cart_item.price * cart_item.quantity
        tax_percentage=TaxesAndCharges.objects.first().tax
        delivery_charges=TaxesAndCharges.objects.first().delivery_charges
        # Recalculate totals for the whole cart
        cart_items = CartItem.objects.filter(user=request.user)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.price * item.quantity for item in cart_items)
        taxes= (tax_percentage/100)*total_price
        grand_total= total_price + taxes + delivery_charges
        all_items_eligible_for_cod = True
        for item in cart_items:
            if not item.is_available_for_cod:
                all_items_eligible_for_cod = False
        return JsonResponse({
            "quantity": cart_item.quantity,
            "subtotal": f"{subtotal:.2f}",
            "removed": False,
            "cart_summary": {
                "total_items": total_items,
                "total_price": f"₹{total_price:.2f}",
                "taxes":f"₹{taxes:.2f}",
                "grand_total":f"₹{grand_total:.2f}"
            },
            'all_items_eligible_for_cod': all_items_eligible_for_cod,
            
        })

    except CartItem.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
