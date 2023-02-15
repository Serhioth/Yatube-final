from django.urls import path
from posts import views
from django.views.decorators.cache import cache_page


app_name = 'posts'

urlpatterns = [
    path(
        'profile/<str:username>/follow/',
        views.FollowView.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.UnfollowView.as_view(),
        name='profile_unfollow'
    ),
    path(
        '',
        cache_page(20, key_prefix='index_page')(
            views.IndexView.as_view(
                template_name='posts/index.html')
        ),
        name='index'
    ),
    path(
        'group/<slug:slug>/',
        cache_page(20, key_prefix='group_list_page')(
            views.GroupView.as_view(
                template_name='posts/group_list.html')
        ),
        name='group_list'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileView.as_view(
            template_name='posts/profile.html'
        ),
        name='profile'
    ),
    path(
        'posts/<int:post_id>/', views.PostDetailView.as_view(
            template_name='posts/post_detail.html'
        ),
        name='post_detail'
    ),
    path(
        'create/', views.PostCreateView.as_view(
            template_name='posts/create_post.html'
        ),
        name='post_create'),
    path(
        'posts/<int:post_id>/edit/', views.PostEditView.as_view(
            template_name='posts/create_post.html'
        ),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/comment/', views.CommentView.as_view(
            template_name='posts/post_detail.html'
        ),
        name='add_comment'
    ),
    path(
        'follow/', views.FollowIndexView.as_view(
            template_name='posts/follow.html'
        ),
        name='follow_index'
    )
]
