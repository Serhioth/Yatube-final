from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DetailView, ListView,
                                  RedirectView, UpdateView)

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


class DataListMixin:
    model = Post
    paginate_by = settings.PER_PAGE


class IndexView(DataListMixin, ListView):

    def get_queryset(self):
        return Post.objects.all()


class GroupPostView(DataListMixin, ListView):

    def get_object(self):
        return get_object_or_404(Group, slug=self.kwargs.get('slug'))

    def get_queryset(self):
        return self.get_object().posts.all()

    def get_context_data(self, **kwargs):
        context = super(GroupPostView, self).get_context_data(**kwargs)
        context['group'] = self.get_object()
        return context


class ProfileView(DataListMixin, ListView):

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        return self.get_object().posts.all()

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['author'] = self.get_object()
        authenticated = self.request.user.is_authenticated
        following = authenticated and Follow.objects.filter(
            user=self.request.user, author=self.get_object()
        ).exists()
        context['following'] = following
        return context


class PostDetailView(DetailView):

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse_lazy(
            'posts/post_detail',
            kwargs={'post_id': post_id}
        )

    def get_comments(self):
        return self.get_object().comments.all()

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = self.get_comments()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.get_username()
        return reverse_lazy(
            'posts:profile',
            kwargs={'username': username}
        )


class PostEditView(LoginRequiredMixin, UpdateView):
    form_class = PostForm

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'posts:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class CommentView(LoginRequiredMixin, CreateView):
    form_class = CommentForm

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_context_data(self, **kwargs):
        context = super(CommentView, self).get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.all()
        context['form'] = CommentForm()
        return context

    def form_valid(self, form):
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = self.request.user
            comment.post = self.get_object()
            comment.save()
            return super().form_valid(form)
        return self.form_class()

    def get_success_url(self):
        post_id = self.get_object().id
        return reverse_lazy(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        )


class FollowView(LoginRequiredMixin, RedirectView):

    def get(self, *args, **kwargs):
        if self.kwargs.get('username') == self.request.user.username:
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.kwargs.get('username')}
                )
            )
        obj, created = Follow.objects.get_or_create(
            author=User.objects.get(username=self.kwargs.get('username')),
            user=self.request.user
        )
        if created:
            return super(FollowView, self).get(*args, **kwargs)
        return redirect(
            reverse_lazy(
                'posts:profile',
                kwargs={'username': self.kwargs.get('username')}
            )
        )

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy(
            'posts:profile_follow',
            kwargs={'username': self.kwargs.get('username')}
        )


class UnfollowView(LoginRequiredMixin, RedirectView):

    def get(self, *args, **kwargs):
        follower = Follow.objects.filter(
            author__username=self.kwargs.get('username'),
            user=self.request.user
        )
        if follower.exists():
            follower.delete()
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.kwargs.get('username')}
                )
            )
        return super(UnfollowView, self).get(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy(
            'posts:profile_unfollow',
            kwargs={'username': self.kwargs.get('username')}
        )


class FollowIndexView(LoginRequiredMixin, DataListMixin, ListView):

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)
