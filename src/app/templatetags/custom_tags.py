from django import template
from app.models import *
from django.db.models import Count, Max, Subquery, OuterRef, F, CharField
from django.utils import timezone
from datetime import datetime
from bleach import linkify
from django.utils.safestring import mark_safe
import re
from app.models import Choice

register = template.Library()

@register.simple_tag
def date_format():
    return timezone.localtime(timezone.now()).strftime('%A')

@register.simple_tag
def get_tags():
    return Tag.objects.values('text').annotate(
        post_count=Count('post'),
        max_post_id=Max('post__id'),
        max_post_title=Max('post__title', output_field=CharField()),
        people_using_tag=Count('post__author', distinct=True),
        last_post_date=Max('post__created_at')
    ).filter(post_count__gt=0).order_by('-post_count')[:7]

@register.filter
def elapsed_time(value):
    current_time = timezone.now()
    time_difference = current_time - value

    if time_difference.total_seconds() < 3600:
        # Less than 1 hour, show in minutes
        minutes = int(time_difference.total_seconds() // 60)
        return f"{minutes}m"
    elif time_difference.total_seconds() < 86400:
        # Less than 24 hours, show in hours
        hours = int(time_difference.total_seconds() // 3600)
        return f"{hours}h"
    elif 1 <= time_difference.days <= 30:
        # Between 1 and 30 days, show in days
        return f"{time_difference.days}d"
    elif 31 <= time_difference.days <= 365:
        # Between 31 days and 1 year, show in months
        months = int(time_difference.days // 30)
        return f"{months}mo"
    else:
        # Over 1 year, show in years
        years = int(time_difference.days // 365)
        return f"{years}y"

@register.filter(needs_autoescape=True)
def linkify_content(text, autoescape=True):
    # Regular expression to find URLs in the text
    url_pattern = r'(https?://\S+)'
    # Replace URLs with clickable links with target="_blank" attribute
    linked_text = re.sub(
        url_pattern, r'<a href="\1" target="_blank">\1</a>', text)
    return linked_text

@register.filter(needs_autoescape=True)
def linkify_content_and_title(text, autoescape=True):
    # Regular expression to find URLs in the text
    url_pattern = r'(https?://\S+)'
    linked_text = re.sub(
        url_pattern, r'<a href="\1" target="_blank">\1</a>', text)
    # Use bleach's linkify to handle additional URLs and email addresses
    linked_text = linkify(linked_text, parse_email=True)
    return mark_safe(linked_text)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def calculate_percentage(value, total):
    try:
        percentage = (value / total) * 100
        return min(percentage, 100)
    except (TypeError, ZeroDivisionError):
        return 0

@register.filter
def remove_hashtags(value):
    return re.sub(r'#\w+', '', value)

@register.filter
def remove_to_username(value):
    return re.sub(r'to:[a-zA-Z0-9_]+', '', value)

@register.filter
def endswith(value, arg):
    return value.endswith(arg)

@register.filter
def find_hashtags(text):
    words = text.split()
    hashtags = [word[1:].lower() for word in words if word.startswith('#')]
    return hashtags

@register.filter
def has_voted_for_post(user, post):
    return any(choice.vote_set.filter(user=user).exists() for choice in post.choice_set.all())

@register.filter
def post_total_votes(value):
    return Post.objects.annotate(total_votes=Count('choice__vote'))
    total_votes_for_poll = post_total_votes.get(id=post.id).total_votes

@register.filter
def limit_users(queryset, limit):
    return queryset[:limit]
