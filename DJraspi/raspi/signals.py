from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import RaspberryPi


@receiver(post_migrate)
def create_singleton(sender, **kwargs):
    if not RaspberryPi.objects.exists():
        raspi = RaspberryPi.objects.create()
        raspi.fill()
        raspi.save()