# Cart Model
from django.conf import settings
from django.db import models
from app.models import Product,Size

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'size')  # Prevent duplicates
        ordering = ['-added_date']

    def __str__(self):
        size_name = f" - {self.size.name}" if self.size else ""
        return f"{self.user} → {self.product.name}{size_name} (x{self.quantity})"

    def get_total_price(self):
        return float(self.quantity) * float(self.product.price)
