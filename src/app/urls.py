from django.urls import path
from . import views

from .views import BookmarkListView,  CategoryListView, SearchView, PostDeleteView, HashtagsView

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    path('post/<int:post_id>/repost/', views.repost_view, name='repost'),


    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),

    path('post/<int:post_pk>/comment/<int:comment_pk>/delete/', views.comment_delete_view, name='comment-delete'),

    path('post/<int:post_pk>/comment/<int:comment_pk>/<int:reply_pk>/delete/', views.reply_delete_view, name='reply-delete'),


    path('search/', views.SearchView.as_view(), name='search'),
    path('hashtags/', HashtagsView.as_view(), name='hashtags'),
    
    path('people_search', views.people_search, name='people_search'),

    

    path('post/<slug:slug>/upvote/', views.upvote, name='upvote'),
    path('post/<slug:slug>/downvote/', views.downvote, name='downvote'),  

    path('accounts/profile/bookmark_list/', BookmarkListView.as_view(),  name='bookmark_list'), 

    path('post/<slug:slug>/add_to_bookmark', views.add_or_remove_bookmark, name='add_to_bookmark'),
    path('post/<slug:slug>/remove_from_bookmark', views.add_or_remove_bookmark, name='remove_from_bookmark'),




    path('create_post/', views.create_post_view, name='create_post'), 

    path('add-choice/<slug:slug>/', views.add_choices, name='add_choices'), 
    path('delete-choice/<int:pk>/', views.delete_choice, name='delete_choice'),

    path('category/<str:category>/', CategoryListView.as_view(), name='tag'), 

    path('group_search/', views.group_search, name='group_search'), 

    


    
]
