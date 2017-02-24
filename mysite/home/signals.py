from .current_user import get_current_user
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Item, Tag, Request, Log
from .serializers import ItemSerializer, TagSerializer, RequestSerializer

    
@receiver(post_save, sender=Item, dispatch_uid="item_save")
def log_item(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=ItemSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,involved_item=instance.id,nature='CREATE '+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,involved_item=instance.id,nature='UPDATE '+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=Item, dispatch_uid="item_delete")
def log_item_delete(sender, instance, **kwargs):
    user = get_current_user()
    log = Log(initiating_user=user.id,involved_item=instance.id,nature='DELETE',timestamp=timezone.now())
    log.save()
        
# Updating tags handled in item logs
# @receiver(post_save, sender=Tag, dispatch_uid="tag_save")
# def log_tag(sender, instance, **kwargs):
#     user = get_current_user()
#     serializer=TagSerializer(instance)
#     log = Log(initiating_user=user.id,nature='UPDATE TAG '+str(serializer.data),timestamp=timezone.now())
#     log.save()
#     
# @receiver(pre_delete, sender=Tag, dispatch_uid="tag_delete")
# def log_tag_delete(sender, instance, **kwargs):
#     user = get_current_user()
#     serializer=TagSerializer(instance)
#     log = Log(initiating_user=user.id,nature='DELETE TAG '+str(serializer.data),timestamp=timezone.now())
#     log.save()
    
@receiver(post_save, sender=Request, dispatch_uid="request_save")
def log_request(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=RequestSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,involved_item=instance.item_id.id,nature='CREATE '+str(serializer.data),timestamp=timezone.now(), related_request=instance.id, affected_user=instance.owner.id)
        log.save()
    else:
        log = Log(initiating_user=user.id,involved_item=instance.item_id.id,nature='UPDATE '+str(serializer.data),timestamp=timezone.now(), related_request=instance.id, affected_user=instance.owner.id)
        log.save()
        
@receiver(pre_delete, sender=Request, dispatch_uid="request_delete")
def log_request_delete(sender, instance, **kwargs):
    user = get_current_user()
    log = Log(initiating_user=user.id,involved_item=instance.item_id.id,nature='DELETE',timestamp=timezone.now(), related_request=instance.id, affected_user=instance.owner.id)
    log.save()
