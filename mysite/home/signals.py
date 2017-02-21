from .current_user import get_current_user
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item, Log
from .serializers import ItemSerializer

    
@receiver(post_save, sender=Item, dispatch_uid="item_save")
def log_item(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=ItemSerializer(instance)
    if created:
        log = Log(initiating_user=user,involved_item=instance,nature='CREATE'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user,involved_item=instance,nature='UPDATE'+str(serializer.data),timestamp=timezone.now())
        log.save()