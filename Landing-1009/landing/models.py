from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image_urls = models.JSONField(default=list, blank=True)
    is_enabled = models.BooleanField(default=True)
    link = models.URLField(default="#", blank=True)

    class Meta:
        verbose_name_plural = "Categories"  # 👈 fixes "Categorys" issue

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
