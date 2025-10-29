from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from app.models import Product,Size
from .models import Cart

# Add to Cart
def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        size = Size.objects.filter(id=size_id).first() if size_id else None

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': f"{product.name} added to cart!",
            'cart_count': request.user.cart_items.count()
        })
    return JsonResponse({'success': False, 'message': 'Failed to add to cart'})


# Get Cart Page
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})


# Increment/Decrement Quantity
def update_cart_quantity(request):
    if request.method == 'POST' and request.user.is_authenticated:
        cart_id = request.POST.get('cart_id')
        action = request.POST.get('action')  # "increment" or "decrement"
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

        if action == 'increment':
            cart_item.quantity += 1
        elif action == 'decrement' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

        total_price = sum(item.get_total_price() for item in Cart.objects.filter(user=request.user))

        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'item_total': cart_item.get_total_price(),
            'total_price': total_price
        })

    return JsonResponse({'success': False})


def remove_cart_item(request):
    if request.method == "POST":
        cart_id = request.POST.get('cart_id')
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.delete()

            # Recalculate total price
            cart_items = Cart.objects.filter(user=request.user)
            total_price = sum(item.get_total_price() for item in cart_items)

            return JsonResponse({
                'success': True,
                'total_price': total_price
            })
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


#### review order