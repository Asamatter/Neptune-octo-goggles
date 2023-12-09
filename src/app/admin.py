from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Post)
admin.site.register(Repost)
admin.site.register(Choice)
admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(Reply)

admin.site.register(Upvote)
admin.site.register(Downvote)

admin.site.register(Bookmark)
admin.site.register(Tag)
admin.site.register(Notification)

