
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(upload_to='images/pfp', blank=True)
    banner = models.ImageField(upload_to='images/banners/', blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(max_length=150, blank=True)
    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers', blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=False)
    is_verify = models.BooleanField(default=False)

    CONTINENT_CHOICES = (
        ('Africa', 'Africa'),
        ('Antarctica', 'Antarctica'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('North America', 'North America'),
        ('Oceania', 'Oceania'),
        ('South America', 'South America'), )

    location = models.CharField(
        max_length=20, choices=CONTINENT_CHOICES, blank=True)

    def __str__(self):
        return self.user.username

    def __str__(self):
        return f'{self.user.username} -followers: {self.followers.count()}'

from .signals import *

class Inbox(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['-created_at']


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.profile.user.username


class Circle(models.Model):
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),]

    host = models.OneToOneField(User, on_delete=models.CASCADE)
    pfp = models.ImageField(upload_to='Circle_pfps/', blank=True, null=True)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='people', blank=True)
    privacy = models.CharField(
        max_length=10, choices=PRIVACY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CirclePost(models.Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=280, blank=True)
    img = models.ImageField(upload_to='circle_post_images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post in {self.circle}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    circlepost = models.ForeignKey(CirclePost, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}: {self.circlepost.title[:20]}'
