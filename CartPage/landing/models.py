from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
class TaxesAndCharges(models.Model):
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    delivery_charges = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"TaxesAndCharges (Tax: {self.tax}%, Delivery: {self.delivery_charges})"
class CartItem(models.Model):
    # Link cart item to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)

    image_url = models.URLField(max_length=500)   # URL of the product image
    name = models.CharField(max_length=200)       # Product name
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price
    color = models.CharField(max_length=50)       # Color of the product
    size = models.CharField(max_length=50)        # Size of the product
    quantity = models.PositiveIntegerField(default=1)  # Quantity in cart
    is_available_for_cod = models.BooleanField(default=True)
    def subtotal(self):
        """Return total price for this cart item"""
        return self.price * self.quantity

    def __str__(self):
        user_info = f"{self.user.username}'s" if self.user else "Guest"
        return f"{user_info} CartItem: {self.name} ({self.quantity})"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If setting this address as default, unset others
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.full_name} - {self.address_line1}, {self.city}"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
