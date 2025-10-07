from django.db import models

from django.contrib.auth.models import User

class CartItem(models.Model):
    # Link cart item to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)

    image_url = models.URLField(max_length=500)   # URL of the product image
    name = models.CharField(max_length=200)       # Product name
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price
    color = models.CharField(max_length=50)       # Color of the product
    size = models.CharField(max_length=50)        # Size of the product
    quantity = models.PositiveIntegerField(default=1)  # Quantity in cart

    def subtotal(self):
        """Return total price for this cart item"""
        return self.price * self.quantity

    def __str__(self):
        user_info = f"{self.user.username}'s" if self.user else "Guest"
        return f"{user_info} CartItem: {self.name} ({self.quantity})"
       
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
