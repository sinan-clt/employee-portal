from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        pass