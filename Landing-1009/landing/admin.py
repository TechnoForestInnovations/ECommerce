# shop/admin.py
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled')
    list_editable = ('is_enabled',)
