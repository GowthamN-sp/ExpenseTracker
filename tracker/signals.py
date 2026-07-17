"""
Signal handlers.

Automatically creates a Profile whenever a new User is created,
and saves the profile whenever the user is saved.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure a profile always exists (defensive, e.g. for pre-existing users)
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()
