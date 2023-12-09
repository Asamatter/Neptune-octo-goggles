from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CircleCreateView, CircleDeleteView

app_name = 'account'
urlpatterns = [
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/<str:username>/',
         views.profile_view, name='profile'),
    path('accounts/profile/<str:username>/edit/',
         views.edit_profile_view, name='edit_profile'),
    path('accounts/profile/<str:username>/remove_pic/',
         views.remove_profile_pic, name='remove_profile_pic'),
    path('accounts/profile/<str:username>/remove_banner/',
         views.remove_banner_pic, name='remove_banner'),
    path('accounts/profile/inbox/<str:username>/', views.inbox, name='inbox'),
    path('inbox/conversation/<str:username>/<int:message_id>/',
         views.conversation, name='conversation'),

    path('accounts/profile/circle/<str:circle_name>/',
         views.circle_detail_view, name='circle-detail'),
    path('accounts/profile/circle/<int:pk>/delete/',
         CircleDeleteView.as_view(), name='circle-delete'),
    path('accounts/profile/cir/create/',
         CircleCreateView.as_view(), name='circle-create'),

    path('accounts/profile/<str:username>/notifications/',
         views.notification, name='notifications'),

    path('accounts/profile/circle/<str:circle_name>/like',
         views.like_view, name='like'),



]
