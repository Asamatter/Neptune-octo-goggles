from django.db import models
from django.contrib.auth.models import User

#automatically add a slug 
from django.utils.text import slugify

from account.models import Profile




# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True) 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    choices_added = models.BooleanField(default=False)

    #automatically add a unique slug 
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            suffix = 1
            
            while Post.objects.filter(slug=unique_slug).exists():
                suffix += 1
                unique_slug = f"{base_slug}-{suffix}"

            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

#TAG
class Tag(models.Model):
    text = models.CharField(max_length=255)
    post = models.ForeignKey(Post, on_delete=models.CASCADE) 

    def __str__(self):
        return f'{self.text}: {self.post.title}'

class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    upvotes = models.ManyToManyField(User, related_name='post_upvotes') #CHANGE 
    
    class Meta:
        unique_together = ('user', 'post') 

    def __str__(self):
        return f'{self.user.username}: {self.post.id}'

   
        
            


class Downvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    downvotes = models.ManyToManyField(User, related_name='post_downvotes') #CHNAGE
    
    class Meta:
        unique_together = ('user', 'post') 

    def __str__(self):
        return f'{self.user.username}: {self.post.title}'


class Choice(models.Model):
    post =  models.ForeignKey(Post, on_delete=models.CASCADE)
    title =  models.CharField(max_length=255)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title  


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('choice', 'user')

    def __str__(self):
        return f'USER: ({self.user.username}): CHOICE({self.choice.title}) - POST({self.choice.post.title} Has {self.choice.post.choice_set.all().count()} choices)'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at =models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="comment_replies")
    
    is_pinned = models.BooleanField(default=False) #add this feature later


    def __str__(self):
        return self.post.title   
        
    class Meta:
        ordering = ['-created_at']

class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.content
        
    class Meta:
        ordering = ['created_at']


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.post.title}: {self.user.username}'
 
    class Meta:
        ordering = ['-created_at']    


class Repost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.original_post.title}'

    class Meta:
        ordering = ['-created_at']    


from account.models import *

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_initiator')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True,null=True)

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)
    follow = models.ForeignKey(Follow, on_delete=models.CASCADE, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    reposted = models.BooleanField(default=False)
    commented = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    followed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.post:
            return self.post.title
        elif self.follow:
            return f"Followed by {self.action_initiator}"
        else:
            return "Notification without a post or follow action"


    class Meta:
        ordering = ['-timestamp']

   


from .signals import *
    