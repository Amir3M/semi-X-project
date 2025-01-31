from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('logout/',LogoutView.as_view(next_page = 'home'), name='logout'), 
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('like/<int:post_id>/', views.LikePostView.as_view(), name='like_post'),
    path('dislike/<int:post_id>/', views.DislikePostView.as_view(), name='dislike_post'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    path('edit/', views.ProfileEditView.as_view(), name='edit_profile'),
    path('send_friend_request/<int:profile_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/<str:action>/<int:user_id>/', views.FriendRequestHandlerView.as_view(), name='handle_friend_request'),
]
