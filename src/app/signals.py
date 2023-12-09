from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from account.models import *

@receiver(post_save, sender=Upvote)
def upvote_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.author:
        Notification.objects.create(
            user=instance.post.author,
            action_initiator=instance.user,
            post=instance.post,
            is_read=False,
            liked=True 
        )

@receiver(post_delete, sender=Upvote)
def upvote_delete_notification(sender, instance, **kwargs):
    Notification.objects.filter(post=instance.post, action_initiator=instance.user).delete()


@receiver(post_save, sender=Repost)
def repost_notification(sender, instance, created, **kwargs):
        if created and instance.user != instance.original_post.author:
            Notification.objects.create(
                user=instance.original_post.author,
                action_initiator=instance.user,
                post=instance.original_post,
                is_read=False,
                reposted=True 
            )

@receiver(post_delete, sender=Repost)
def repost_delete_notification(sender, instance, **kwargs):
    Notification.objects.filter(post=instance.original_post, action_initiator=instance.user).delete()


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
        if created and instance.user != instance.post.author:
            Notification.objects.create(
                user=instance.post.author,
                action_initiator=instance.user,
                post=instance.post,
                comment=instance,
                is_read=False,
                commented=True 
            )



@receiver(post_save, sender=Follow)
def following_notification(sender, instance, created, **kwargs):
    if created:
                Notification.objects.create(
                    user=instance.profile.user,  
                    action_initiator=instance.user,  
                    follow=instance,
                    is_read=False,
                    followed=True 
                )
          
import re
@receiver(post_save, sender=Reply)
def reply_notification(sender, instance, created, **kwargs):
   
            content = instance.content
            match = re.search(r'to:([^ ]+)', content)
           
            if match:
                # Extract the username from the match
                username = match.group(1)

               
                mentioned_user = User.objects.get(username=username)
        

                Notification.objects.create(
                    user=mentioned_user, 
                    action_initiator=instance.user,
                    post=instance.comment.post,
                    comment=instance.comment,
                    reply=instance,
                    is_read=False,
                    replied=True 
                )

