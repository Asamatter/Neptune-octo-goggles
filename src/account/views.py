from datetime import datetime, timedelta
from django.db.models.functions import Coalesce
from django.db.models import Q, F, Value, BooleanField, Case, When, ExpressionWrapper, DateTimeField
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from account.tokens import account_activation_token
from django.db.models import Q
import datetime
from django.views.generic import DetailView, CreateView, DeleteView
import json
from django.http import JsonResponse
from django.urls import reverse
from app.models import *
from django.contrib.sessions.models import Session
import os


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data['email']
            user.email = email
            user.save()
            messages.success(request, 'Registration completed successfully.')
            return redirect('account:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('account:profile', username=username)
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    current_user_profile = request.user.profile
    new_message = Inbox.objects.filter(
        receiver=profile.user, is_read=False).count()
    is_following = current_user_profile.following.filter(
        user=profile.user).exists()
    files_uploaded_by_user_count = Post.objects.filter(
        Q(file__isnull=False) & ~Q(file=''), author=profile.user).count()

    profile_id = str(profile.id)
    view_count = request.session.get(f'profile_view_counts_{profile_id}', 0)
    view_count += 1
    request.session[f'profile_view_counts_{profile_id}'] = view_count
    request.session[profile_id] = True
    request.session.save()

    user_reposts = Repost.objects.filter(user=profile.user)
    reposted_post_ids = user_reposts.values_list('original_post', flat=True)

    user_posts_with_reposts = Post.objects.filter(
        Q(id__in=profile.user.post_set.values_list('id', flat=True)) |
        Q(id__in=reposted_post_ids) |
        Q(repost__user=profile.user,
          repost__original_post__in=profile.user.post_set.all())
    ).distinct()

    user_posts_with_reposts = user_posts_with_reposts.annotate(
        is_repost=Case(
            When(Q(repost__user=profile.user) | Q(
                id__in=reposted_post_ids), then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        repost_timestamp=Case(
            When(Q(repost__user=profile.user) | Q(
                id__in=reposted_post_ids), then=F('repost__created_at')),
            default=Value(None),
            output_field=DateTimeField()
        ))

    user_posts_with_reposts = user_posts_with_reposts.filter(
        Q(is_repost=True) | Q(author=profile.user))

    combined_items = list(user_posts_with_reposts)
    combined_items.sort(
        key=lambda item: item.repost_timestamp if item.is_repost else item.created_at, reverse=True)

    unique_posts = []
    unique_reposts_set = set()

    for item in combined_items:
        if item.id not in unique_reposts_set:
            unique_reposts_set.add(item.id)
            unique_posts.append(item)

    if 'toggle_active' in request.POST:
        profile.is_active = not profile.is_active
        profile.save()
        return JsonResponse({'success': True})

    elif 'follow_unfollow' in request.POST:
        if is_following:
            # remove from followers
            profile.followers.remove(current_user_profile)
            current_user_profile.following.remove(
                profile)  # remove it from following list
            Follow.objects.filter(profile=profile, user=request.user).delete()
        else:
            profile.followers.add(current_user_profile)
            current_user_profile.following.add(profile)
            Follow.objects.create(profile=profile, user=request.user)
        return JsonResponse({'success': True})

    context = {
        'unique_posts': unique_posts,
        'view_count': view_count,
        'profile': profile,
        'is_following': is_following,
        'new_message': new_message,
        'files_uploaded_by_user_count': files_uploaded_by_user_count, }
    return render(request, 'profile.html', context)


def edit_profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account:profile', username=username)
    else:
        form = ProfileForm(instance=profile)
    context = {'form': form, 'profile': profile}
    return render(request, 'edit_profile.html', context)


def remove_profile_pic(request, username):
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        profile.pic.delete(save=True)
        return JsonResponse({'success': True})


def remove_banner_pic(request, username):
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        profile.banner.delete(save=True)
        return JsonResponse({'success': True})


def inbox(request, username):
    receiver = get_object_or_404(User, username=username)
    logged_in_user = request.user
    senders = Inbox.objects.filter(receiver=logged_in_user).values_list(
        'sender__username', flat=True).distinct()

    all_participants = set(list(senders) )
    last_messages = {}
    unread_messages_count_by_user = {}

    for participant_username in all_participants:
        participant_user = User.objects.get(username=participant_username)
        last_message = Inbox.objects.filter(
            Q(sender=participant_user, receiver=logged_in_user) | Q(
                sender=logged_in_user, receiver=participant_user)
        ).latest('created_at')
        last_messages[participant_username] = last_message
        if last_message:
            unread_messages = Inbox.objects.filter(
                Q(sender=participant_user, receiver=logged_in_user), is_read=False)
            unread_messages_count = unread_messages.count()
            unread_messages_count_by_user[participant_username] = unread_messages_count

    unread_messages_count = 0
    context = {
        'username': username,
        'unread_messages_count': unread_messages_count,
        'unread_messages_count_by_user': unread_messages_count_by_user,
        'last_messages': last_messages, }
    return render(request, 'inbox.html', context)


def conversation(request, username, message_id):
    receiver = get_object_or_404(User, username=username)
    sender = request.user
    messages = Inbox.objects.filter((Q(sender=sender) & Q(receiver=receiver)) | (
        Q(sender=receiver) & Q(receiver=sender)))

    messages_count = messages.count

    mark_as_read = request.GET.get('mark_as_read')
    if mark_as_read == 'true':
        participant_user = User.objects.get(username=username)
        logged_in_user = request.user
        Inbox.objects.filter(
            sender=participant_user, receiver=logged_in_user).update(is_read=True)

    if request.method == 'POST':
        form = InboxForm(request.POST)
        if form.is_valid():
            inbox = form.save(commit=False)
            inbox.sender = request.user
            inbox.receiver = receiver
            inbox.save()
            return JsonResponse({'success': True})
    else:
        form = InboxForm()
    context = {
        'messages_count': messages_count,
        'messages': messages,
        'form': form,
        'username': username,
        'message_id': message_id}
    return render(request, 'all_messages.html', context)


@login_required
def circle_detail_view(request, circle_name):
    circle_obj = get_object_or_404(Circle, name=circle_name)
    circle_posts = CirclePost.objects.filter(circle=circle_obj)

    if request.method == 'POST':
        user = request.user
        has_joined = circle_obj.members.filter(username=user.username).exists()
        circle_post_form = CirclePostForm(request.POST, request.FILES)

        if 'join_leave' in request.POST:
            if has_joined:
                circle_obj.members.remove(user)
            else:
                circle_obj.members.add(user)
            return JsonResponse({'success': True})

        elif 'create_circle_post' in request.POST:
            if circle_post_form.is_valid():
                circle_post = circle_post_form.save(commit=False)
                circle_post.circle = circle_obj
                circle_post.user = request.user
                circle_post.save()
                return redirect('account:circle-detail', circle_obj.name)

    circle_post_form = CirclePostForm()
    context = {
        "circle_obj": circle_obj,
        "circle_posts": circle_posts,
        "circle_post_form": circle_post_form,
    }

    return render(request, 'circle.html', context)


class CircleCreateView(CreateView):
    model = Circle
    form_class = CircleCreationForm
    template_name = 'circle_form.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        user = self.request.user
        if form.is_valid():
            if Circle.objects.filter(host=user).exists():
                return redirect('account:circle-create')
            circle = form.save(commit=False)
            circle.host = user
            circle.save()
            circle.members.add(user)
            return redirect('account:circle-detail', circle.name)
        return self.form_invalid(form)


class CircleDeleteView(DeleteView):
    model = Circle
    template_name = 'circle_confirm_delete.html'

    def get_success_url(self):
        return reverse('account:profile', kwargs={'username': self.request.user.username})


# LIKE
def like_view(request, circle_name):
    if request.method == 'POST':
        post_pk = request.POST.get('circle_post')
        post = get_object_or_404(CirclePost, pk=post_pk)
        liked = Like.objects.filter(
            user=request.user, circlepost=post).exists()
        if liked:
            Like.objects.filter(user=request.user, circlepost=post).delete()
        else:
            Like.objects.create(user=request.user, circlepost=post)
        return JsonResponse({'success': True})


def notification(request, username):
    notifications = Notification.objects.filter(user=request.user)
    profile = get_object_or_404(Profile, user__username=username)

    mark_as_read = request.GET.get('mark_as_read')
    if mark_as_read == 'true':
        Notification.objects.filter(user=request.user).update(is_read=True)

    context = {'notifications': notifications, 'profile': profile}
    return render(request, 'notification_list.html', context)
