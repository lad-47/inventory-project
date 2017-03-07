from .current_user import get_current_user
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Item, Tag, User, CustomFieldEntry,CustomShortTextField, CustomLongTextField, CustomIntField, CustomFloatField, Cart_Request, Request, Log
from .serializers import ItemSerializer, UserSerializer, TagSerializer, RequestSerializer, CustomFieldEntrySerializer, CustomShortTextFieldSerializer, CustomLongTextFieldSerializer, CustomIntFieldSerializer, CustomFloatFieldSerializer

    
@receiver(post_save, sender=Item, dispatch_uid="item_save")
def log_item(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=ItemSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='CREATE Item'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='UPDATE Item'+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=Item, dispatch_uid="item_delete")
def log_item_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=ItemSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='DELETE Item'+str(serializer.data),timestamp=timezone.now())
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
    
@receiver(post_save, sender=Cart_Request, dispatch_uid="request_save")
def log_request(sender, instance, created, **kwargs):
    user = get_current_user()
    subrequests = Request.objects.filter(parent_cart=instance)
    info = "for "+instance.cart_owner.username+": "
    for subrequest in subrequests:
        info+=subrequest.item_id.item_name+" x"+str(subrequest.quantity)+" "
    info+="STATUS: "+instance.cart_status
    if not instance.cart_status=='P':
        if created:
            log = Log(initiating_user=user.id,initiating_username=user.username,nature='CREATE Request '+info,timestamp=timezone.now(), related_request=instance.id, affected_user=instance.cart_owner.id, affected_username=instance.cart_owner.username)
            log.save()
        else:
            log = Log(initiating_user=user.id,initiating_username=user.username,nature='UPDATE Request '+info,timestamp=timezone.now(), related_request=instance.id, affected_user=instance.cart_owner.id, affected_username=instance.cart_owner.username)
            log.save()
    
        
@receiver(pre_delete, sender=Cart_Request, dispatch_uid="request_delete")
def log_request_delete(sender, instance, **kwargs):
    user = get_current_user()
    log = Log(initiating_user=user.id,initiating_username=user.username,nature='DELETE Request',timestamp=timezone.now(), related_request=instance.id, affected_user=instance.cart_owner.id, affected_username=instance.cart_owner.username)
    log.save()
    
@receiver(post_save, sender=User, dispatch_uid="user_save")
def log_user(sender, instance, created, **kwargs):
    user = get_current_user()
    if user.is_anonymous==True:
        user=instance
    serializer=UserSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,nature='CREATE User'+str(serializer.data),timestamp=timezone.now(), affected_user=instance.id, affected_username=instance.username)
        log.save()
    else:
#         log = Log(initiating_user=user.id,nature='UPDATE User'+str(serializer.data),timestamp=timezone.now(), affected_user=instance.id)
#         log.save()
        pass
    
    
@receiver(pre_delete, sender=User, dispatch_uid="user_delete")
def log_user_delete(sender, instance, **kwargs):
    user = get_current_user()
    log = Log(initiating_user=user.id,initiating_username=user.username,nature='DELETE User',timestamp=timezone.now(), affected_user=instance.id, affected_username=instance.username)
    log.save()
    
@receiver(post_save, sender=CustomFieldEntry, dispatch_uid="field_save")
def log_field(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=CustomFieldEntrySerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,nature='CREATE Custom Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,nature='UPDATE Custom Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=CustomFieldEntry, dispatch_uid="field_delete")
def log_field_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=CustomFieldEntrySerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,nature='DELETE Custom Field'+str(serializer.data),timestamp=timezone.now())
    log.save()
    
@receiver(post_save, sender=CustomShortTextField, dispatch_uid="short_save")
def log_short(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=CustomShortTextFieldSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='CREATE Short Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='UPDATE Short Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=CustomShortTextField, dispatch_uid="short_delete")
def log_short_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=CustomShortTextFieldSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='DELETE Short Field'+str(serializer.data),timestamp=timezone.now())
    log.save()
    
@receiver(post_save, sender=CustomLongTextField, dispatch_uid="long_save")
def log_long(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=CustomLongTextFieldSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='CREATE Long Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='UPDATE Long Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=CustomLongTextField, dispatch_uid="long_delete")
def log_long_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=CustomLongTextFieldSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='DELETE Long Field'+str(serializer.data),timestamp=timezone.now())
    log.save()
    
@receiver(post_save, sender=CustomIntField, dispatch_uid="int_save")
def log_int(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=CustomIntFieldSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='CREATE Int Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='UPDATE Int Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=CustomIntField, dispatch_uid="int_delete")
def log_int_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=CustomIntFieldSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='DELETE Int Field'+str(serializer.data),timestamp=timezone.now())
    log.save()
    
@receiver(post_save, sender=CustomFloatField, dispatch_uid="float_save")
def log_float(sender, instance, created, **kwargs):
    user = get_current_user()
    serializer=CustomFloatFieldSerializer(instance)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='CREATE Float Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='UPDATE Float Field'+str(serializer.data),timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=CustomFloatField, dispatch_uid="float_delete")
def log_float_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=CustomFloatSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='DELETE Float Field'+str(serializer.data),timestamp=timezone.now())
    log.save()
    

    