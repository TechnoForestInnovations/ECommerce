from django.contrib import admin
from .models import Product, ProductImage,ProductSize

class ProductImageInline(admin.TabularInline):  # or StackedInline for bigger preview
    model = ProductImage
    extra = 5   # number of empty image fields shown
class ProductSizeInline(admin.TabularInline):
    model = ProductSize

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'colour','season', 'price')
    inlines = [ProductImageInline,ProductSizeInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "stock")

