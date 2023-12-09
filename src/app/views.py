from django.views import View
from django.urls import reverse_lazy
from account.models import *
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.urls import reverse
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q  
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from django.db.models import Count, Sum
from account.models import Inbox
from django.views.generic import ListView, DeleteView
from django.views.generic import TemplateView

def home(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    profiles = Profile.objects.all()
    active_users = Profile.objects.filter(is_active=True).count()
    unread_noti = 0

    for profile in profiles:
        if request.user.is_authenticated:
            username = request.user.username
            profile = get_object_or_404(Profile, user__username=username)
    new_message = Inbox.objects.filter(
        receiver=profile.user, is_read=False).count()

    if request.method == 'POST':
        post_slug = request.POST.get('post_slug')
        choice_id = request.POST.get('choice')
        if choice_id:
            choice = get_object_or_404(Choice, pk=choice_id)
            post = get_object_or_404(Post, slug=post_slug)
            existing_vote = Vote.objects.filter(
                choice__post=post, user=request.user).exists()
            if existing_vote:
                return JsonResponse({'success': False, 'error': 'You have already voted for a different option in this post.'})
            vote, created = Vote.objects.get_or_create(
                choice=choice, user=request.user)
            vote_count = choice.vote_set.count()
            return JsonResponse({'success': True, 'post_id': post.id, 'vote_count': vote_count, 'has_voted': True, })

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.choices_added = True
            post.author = request.user
            post.save()
            return JsonResponse({'success': True,
                                 'data': {
                                     'title': post.title,
                                     'author': request.user.username,
                                     'created_at': post.created_at,
                                     'post_id': post.id,
                                     'upvotes': post.upvote_set.count(),
                                     'downvotes': post.downvote_set.count(),

                                 }})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = PostForm()

    post_view_counts = request.session.get('post_view_counts', {})
    posts_with_view_counts = []

    post_total_votes = Post.objects.annotate(total_votes=Count('choice__vote'))
    total_votes_for_poll = 0  # Initialize outside the loop
    for post in posts:
        profile = post.author.profile
        view_count = post_view_counts.get(str(post.id), 0)
        posts_with_view_counts.append({'post': post, 'view_count': view_count})
        total_votes_for_poll = post_total_votes.get(id=post.id).total_votes

        comments = post.comments.prefetch_related('replies').all()
        total_comment_count = comments.count(
        ) + sum([comment.replies.count() for comment in comments])
        post.total_comment_count = total_comment_count

        # VOTING
        if request.user.is_authenticated:
            post.has_voted = Vote.objects.filter(
                choice__post=post, user=request.user).exists()
        else:
            post.has_voted = False

        if request.user.is_authenticated:
            post.bookmark_exists = Bookmark.objects.filter(
                user=request.user, post=post).exists()
            post.has_reposted = Repost.objects.filter(
                user=request.user, original_post=post).exists()

    if request.user.is_authenticated:
        unread_noti = Notification.objects.filter(
            user=request.user, is_read=False).count()

    context = {'new_message': new_message,
               'profile': profile,
               'unread_noti': unread_noti,
               'total_votes_for_poll': total_votes_for_poll,
               'posts': posts, 'user': request.user,
               'form': form,
               'posts_with_view_counts': posts_with_view_counts,
               'post_total_votes': post_total_votes}
    return render(request, 'index.html', context)

# VOTE/DOWNVOTE
def upvote(request, slug):
    post = get_object_or_404(Post, slug=slug)
    upvote_count = post.upvote_set.count()
    downvote_count = post.downvote_set.count()

    if request.method == 'POST':
        user = request.user
        upvote, created = Upvote.objects.get_or_create(user=user, post=post)

        if created:
            Downvote.objects.filter(user=user, post=post).delete()
        else:
            upvote.delete()
        upvote_count = post.upvote_set.count()
        downvote_count = post.downvote_set.count()
    return JsonResponse({'post_id': post.id, 'upvote_count': upvote_count, 'downvote_count': downvote_count})

def downvote(request, slug):
    post = get_object_or_404(Post, slug=slug)
    upvote_count = post.upvote_set.count()
    downvote_count = post.downvote_set.count()

    if request.method == 'POST':
        user = request.user
        downvote, created = Downvote.objects.get_or_create(
            user=user, post=post)

        if created:
            Upvote.objects.filter(user=user, post=post).delete()
        else:
            downvote.delete()

        upvote_count = post.upvote_set.count()
        downvote_count = post.downvote_set.count()

    return JsonResponse({'post_id': post.id, 'upvote_count': upvote_count, 'downvote_count': downvote_count})


# SEARCH
class SearchView(TemplateView):
    template_name = 'search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        results = []

        if query:
            results = Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query))

        context['query'] = query
        context['results'] = results
        return context

    def render_to_response(self, context):
        search_results = render_to_string(self.template_name, context)
        return HttpResponse(search_results)


@login_required(login_url='account:login')
def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    post_id = post.id
    post_view_counts = request.session.get('post_view_counts', {})
    view_count = post_view_counts.get(str(post_id), 0)
    view_count += 1
    post_view_counts[str(post_id)] = view_count
    request.session['post_view_counts'] = post_view_counts
    request.session.save()

    post_total_votes = Post.objects.annotate(total_votes=Count('choice__vote'))
    total_votes_for_poll = post_total_votes.get(id=post.id).total_votes

    if request.method == 'POST':
        action = request.POST.get('action', '')
        comment_Form = CommentForm(request.POST)

        reply_content = request.POST.get('reply_content')

        if action == 'comment_submit':
            reply_form = ReplyForm()

            if comment_Form.is_valid():
                content = comment_Form.cleaned_data.get('content')
                comment = Comment(
                    post=post, user=request.user, content=content)
                comment.save()

                return JsonResponse({'success': True, })
            else:
                comment_Form = CommentForm()

        if action == 'reply_submit':
            reply_form = ReplyForm(request.POST)

            if reply_form.is_valid():
                comment_id = request.POST.get('comment_id')
                comment = get_object_or_404(Comment, id=comment_id, post=post)
                new_reply = reply_form.save(commit=False)
                new_reply.user = request.user
                new_reply.comment = comment

                new_reply.metadata = {'reply_content': reply_content}

                new_reply.save()

                return JsonResponse({'success': True})
            else:
                reply_form = ReplyForm()

    comments = post.comments.prefetch_related('replies').all()
    total_comment_count = comments.count(
    ) + sum([comment.replies.count() for comment in comments])

    post.has_reposted = Repost.objects.filter(
        user=request.user, original_post=post).exists()

    choices = post.choice_set.all()
    if request.user.is_authenticated:
        has_voted = Vote.objects.filter(
            choice__post=post, user=request.user).exists()
    else:
        has_voted = False

    reply_form = ReplyForm()
    comment_Form = CommentForm()
    context = {'total_comment_count': total_comment_count, 'reply_form': reply_form, 'post': post, 'total_votes_for_poll': total_votes_for_poll, 'post_total_votes': post_total_votes, 'choices': choices, 'has_voted':
               has_voted, 'comment_Form': comment_Form, 'view_count': view_count, 'comments': comments}
    return render(request, 'post_detail.html', context)


def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            content = request.POST.get('content')
            tags = content.split()
            unique_tags = set()
            for tag_text in tags:
                if tag_text.startswith('#'):
                    cleaned_tag = tag_text.strip('#').strip()
                    if len(cleaned_tag) > 1:
                        cleaned_tag_lower = cleaned_tag.lower()
                        if cleaned_tag_lower not in unique_tags:
                            unique_tags.add(cleaned_tag_lower)
                            post.author = request.user
                            post.save()
                            tag = Tag.objects.create(
                                text=cleaned_tag_lower, post=post)

            post.author = request.user
            post.save()

            if 'skip' in request.POST:
                post.choices_added = True
                post.save()
                return redirect('home')

            post.choices_added = False
            post.save()
            return redirect('add_choices', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


def add_choices(request, slug):
    post = Post.objects.get(slug=slug)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.post = post
            choice.save()

            # add_options
            if 'send' in request.POST:

                if post.choice_set.count() > 1:
                    post.choices_added = True
                    post.save()
                    return redirect('home')
            else:
                return JsonResponse({'success': True, })

    else:
        form = ChoiceForm(initial={'title': ' Enter choice'})
    return render(request, 'add_choices.html', {'form': form, 'post': post})


def delete_choice(request, pk):
    choice = get_object_or_404(Choice, pk=pk)
    post = choice.post
    choice.delete()
    return JsonResponse({'success': True, })

# BOOKMARK
@method_decorator(login_required(login_url='account:login'), name='dispatch')
class BookmarkListView(ListView):
    model = Bookmark
    template_name = 'bookmark.html'
    context_object_name = 'bookmarks'

    def get_queryset(self):
        user = self.request.user
        return Bookmark.objects.filter(user=user)

def add_or_remove_bookmark(request, slug):
    post = get_object_or_404(Post, slug=slug)
    user = request.user

    if request.method == 'POST':
        bookmark_exists = Bookmark.objects.filter(
            user=user, post=post).exists()

        if bookmark_exists:
            Bookmark.objects.filter(user=user, post=post).delete()
            bookmark_added = False
        else:
            Bookmark.objects.create(user=user, post=post)
            bookmark_added = True

        response = {'bookmark_added': bookmark_added,
                    'post_bookmark_count': post.bookmark_set.all().count(),
                    'bookmark_user_count': user.bookmark_set.all().count(),
                    'post_id': post.id,

                    }
        return JsonResponse(response)
    return JsonResponse({'error': 'Invalid request'})


# TAG
class CategoryListView(ListView):
    model = Post
    template_name = 'category.html'
    context_object_name = 'post_tags'

    def get_queryset(self):
        category = self.kwargs['category']
        return Post.objects.filter(tag__text=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs['category']
        context['tag_title'] = category
        context['count'] = Post.objects.filter(tag__text=category).count()
        post_view_counts = self.request.session.get('post_view_counts', {})
        posts_with_view_counts = []

        category_id = category
        tag_view_counts = self.request.session.get('tag_view_counts', {})
        view_count = tag_view_counts.get(str(category_id), 0)
        view_count += 1
        tag_view_counts[str(category_id)] = view_count
        self.request.session['tag_view_counts'] = tag_view_counts
        self.request.session.save()

        voted_choices = []
        if self.request.user.is_authenticated:
            user = self.request.user
            voted_choices = Vote.objects.filter(
                user=user).values_list('choice__post__id', flat=True)

        post_total_votes = Post.objects.annotate(
            total_votes=Count('choice__vote'))
        total_votes_for_poll = 0

        tags = Tag.objects.values('text').annotate(
            tag_contributors=Count('post__author', distinct=True))

        for post in context['post_tags']:
            post.has_voted = post.id in voted_choices

            view_count = post_view_counts.get(str(post.id), 0)
            posts_with_view_counts.append(
                {'post': post, 'view_count': view_count})
            total_votes_for_poll = post_total_votes.get(id=post.id).total_votes

            comments = post.comments.prefetch_related('replies').all()
            total_comment_count = comments.count(
            ) + sum([comment.replies.count() for comment in comments])
            post.total_comment_count = total_comment_count

        context['total_votes_for_poll'] = total_votes_for_poll
        context['post_total_votes'] = post_total_votes
        context['posts_with_view_counts'] = posts_with_view_counts
        context['tag_view_counts'] = tag_view_counts
        context['tags'] = tags
        return context


def group_search(request):
    circles = Circle.objects.all()
    query = request.GET.get('query')
    results = circles

    if query:
        results = circles.filter(name__icontains=query)

    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)
    context = {'results': results}
    return render(request, 'group_search.html', context)


def people_search(request):
    users = User.objects.all().order_by('-last_login')
    query = request.GET.get('query')
    results = users[:5]

    if query:
        results = users.filter(username__icontains=query)

    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)
    context = {'results': results}
    return render(request, 'people_search.html', context)


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('home')


def comment_delete_view(request, post_pk, comment_pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, post_id=post_pk, id=comment_pk)
        comment.delete()
        return JsonResponse({'success': True, 'commentsCount': Comment.objects.filter(post_id=post_pk).count()})
    else:
        return JsonResponse({'error': 'Invalid method'})


def reply_delete_view(request, post_pk, comment_pk, reply_pk):
    if request.method == 'POST':
        reply = get_object_or_404(Reply, comment_id=comment_pk, id=reply_pk)
        reply.delete()
        return JsonResponse({'success': True, })
    else:
        return JsonResponse({'error': 'Invalid method'})


def repost_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get('content')

        repost, created = Repost.objects.get_or_create(
            user=request.user, original_post=post)
        repost.content = content
        repost.save()
        if created:
            return JsonResponse({'success': True, })
        else:
            repost.delete()
            return JsonResponse({'success': True, 'message': 'Repost removed'})


class HashtagsView(TemplateView):
    template_name = 'hashtags.html'
