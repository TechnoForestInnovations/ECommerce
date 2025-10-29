from django.shortcuts import render, redirect
from cart.models import Cart  # Assuming address model exists
from django.contrib.auth.decorators import login_required



@login_required
def confirm_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    # try:
    #     pass
    #     # address = Address.objects.filter(user=request.user).first()
    # except:
    #     address = None

    if not cart_items:
        return redirect('cart')  # If no items, go back to cart

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        # 'address': address
    }
    return render(request, 'orders/confirm_order.html', context)



# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from orders.models import  Order

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def razorpay_payment(request):
    if request.method == "POST":
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return redirect('cart')

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        amount = int(total_price * 100)  # convert to paise

        # Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        # ✅ Create Order records in your DB (for each cart item)
        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                total_price=item.product.price * item.quantity,
                payment_method='razorpay',
                status='pending',
                razorpay_order_id=razorpay_order['id']
            )

        context = {
            'cart_items': cart_items,
            'amount': amount,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'total_price': total_price,
        }

        return render(request, 'orders/razorpay_payment.html', context)

    return redirect('cart')



# views.py
@csrf_exempt
def razorpay_success(request):
    if request.method == "POST":
        # Update order status, clear cart, etc.
        return render(request, 'orders/payment_success.html')
    return redirect('cart')





from django.shortcuts import render
from orders.models import Order

def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


