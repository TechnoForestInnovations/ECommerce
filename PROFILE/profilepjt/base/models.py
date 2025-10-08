from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, default='default.png', blank=True)
    phone = models.CharField(max_length=30, blank=True)
    # optional: add extra fields if needed
    def __str__(self):
        return self.user.username

# signals to create profile on user creation
from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # ensure profile exists (safe)
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
