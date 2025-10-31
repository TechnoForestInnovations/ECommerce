from django.contrib import admin

# Register your models here.
from . models import Cart


@admin.register(Cart)
class ProductStockAdmin(admin.ModelAdmin):
    # list_display = ('product', 'size', 'stock')
    list_filter = ('size', 'product')