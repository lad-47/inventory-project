from .current_user import get_current_user
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import *
from .serializers import ItemSerializer, UserSerializer, TagSerializer, RequestSerializer, CustomFieldEntrySerializer, CustomShortTextFieldSerializer, CustomLongTextFieldSerializer, CustomIntFieldSerializer, CustomFloatFieldSerializer
from django.core.mail import EmailMessage
  
@receiver(post_save, sender=Asset, dispatch_uid="asset_save")
def log_asset(sender, instance, created, **kwargs):
    user = get_current_user()
    info = instance.item_name+", asset_tag: "+str(instance.asset_tag)
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='CREATE Asset '+info,timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='UPDATE Asset '+info,timestamp=timezone.now())
        log.save()
        
@receiver(pre_delete, sender=Asset, dispatch_uid="asset_delete")
def log_asset_delete(sender, instance, **kwargs):
    user = get_current_user()
    serializer=AssetSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='DELETE Asset'+str(serializer.data),timestamp=timezone.now())
    log.save()  
    
@receiver(post_save, sender=Item, dispatch_uid="item_save")
def log_item(sender, instance, created, **kwargs):
    user = get_current_user()
    info = instance.item_name+", count: "+str(instance.count)+", minimum stock: "+str(instance.minimum_stock)+", model number: "+instance.model_number+", description: "+instance.description+", is asset?: "+str(instance.is_asset)+", tags: "
    tag_count=0
    for tag in instance.tags.all():
        info+=tag.tag+", "
        tag_count+=1      
    info=info[:-2]
    if tag_count==0:
        info=info[:-6]
    if created:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='CREATE Item '+info,timestamp=timezone.now())
        log.save()
    else:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.id,involved_item_name=instance.item_name,nature='UPDATE Item '+info,timestamp=timezone.now())
        log.save()
    
    ## check minimum stock
    if instance.count<instance.minimum_stock and not instance.understocked:
        instance.understocked = True
        instance.save()
        message="The available pool for "+instance.item_name+" has fallen below the minimum stock threshold of "+str(instance.minimum_stock)+". Only "+str(instance.count)+" are still available."
        tag=EmailTag.objects.all()[0].tag
        subscribed_emails=SubscribedEmail.objects.all()
        bcc=[]
        for email in subscribed_emails:
            bcc.append(email.email)
        email = EmailMessage(
            tag+' Restock Reminder',
            message,
            'from@example.com',
            ['duke.ece.inventory@gmail.com'],
            bcc
        )
        email.send()
    elif instance.count>=instance.minimum_stock and instance.understocked:
        instance.understocked = False
        instance.save()
        
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

@receiver(post_save, sender=Request, dispatch_uid="request_save")
def log_request(sender, instance, created, **kwargs):
    user = get_current_user()
    to_log=False
    if instance.status=='Z':
        info = 'Loan of '+instance.item_id.item_name+" x"+str(instance.quantity)+" converted to disbursement"
        to_log=True
    elif instance.status=='R':
        info = 'Loan of '+instance.item_id.item_name+" x"+str(instance.quantity)+" returned"
        to_log=True
    if to_log:
        log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.item_id.id,involved_item_name=instance.item_id.item_name,nature=info,timestamp=timezone.now(), related_request=instance.parent_cart.id, affected_user=instance.owner.id, affected_username=instance.owner.username)
        log.save()
    
@receiver(post_save, sender=Cart_Request, dispatch_uid="cart_request_save")
def log_cart_request(sender, instance, created, **kwargs):
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
    serializer=CustomFloatFieldSerializer(instance)
    log = Log(initiating_user=user.id,initiating_username=user.username,involved_item=instance.parent_item.id,involved_item_name=instance.parent_item.item_name,nature='DELETE Float Field'+str(serializer.data),timestamp=timezone.now())
    log.save()
    

    