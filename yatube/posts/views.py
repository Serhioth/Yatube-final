from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DetailView, ListView, UpdateView,
                                  RedirectView)
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from django.conf import settings


class IndexView(ListView):
    model = Post
    paginate_by = settings.PER_PAGE
    posts = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        paginator = Paginator(self.posts, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context['title'] = 'Последние обновления на сайте'
        context['page_obj'] = page_obj
        return context


class GroupPostView(ListView):
    model = Group
    paginate_by = settings.PER_PAGE

    def get_object(self):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return group

    def get_queryset(self):
        group_posts = Post.objects.filter(group__slug=self.kwargs['slug'])
        return group_posts

    def get_context_data(self, **kwargs):
        context = super(GroupPostView, self).get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context['title'] = f'Сообщения группы {self.get_object().title}'
        context['description'] = self.get_object().description
        context['group'] = self.get_object()
        context['page_obj'] = page_obj
        return context


User = get_user_model()


class ProfileView(ListView):
    model = User
    paginate_by = settings.PER_PAGE

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user

    def get_queryset(self):
        user_posts = self.get_object().posts.all()
        return user_posts

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context['title'] = (
            f'Профиль пользователя {self.get_object().get_full_name()}'
        )
        context['author'] = self.get_object()
        context['page_obj'] = page_obj
        authenticated = self.request.user.is_authenticated
        following = authenticated and Follow.objects.filter(
            user=self.request.user, author=self.get_object()
        ).exists()
        context['following'] = following
        return context


class PostDetailView(DetailView):
    model = Post

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        success_url = reverse_lazy(
            'posts/post_detail',
            kwargs={'post_id': post_id}
        )
        return success_url

    def get_comments(self):
        comments = self.get_object().comments.all()
        return comments

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['title'] = str(self.get_object())
        context['post'] = self.get_object()
        context['comments'] = self.get_comments
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    title = 'Создание новой записи'

    def form_valid(self, form):
        if form.is_valid():
            post = form.save(commit=False)
            post.author = self.request.user
            post.save()
            return super().form_valid(form)
        return self.form_class()

    def get_success_url(self):
        username = self.request.user.get_username()
        success_url = reverse_lazy(
            'posts:profile',
            kwargs={'username': username}
        )
        return success_url

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context


class PostEditView(LoginRequiredMixin, UpdateView):
    template = 'posts/create_post.html'
    model = Post
    title = 'Редактирование записи'
    form_class = PostForm

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['post'] = self.get_object()
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        return self.form_class()

    def get_success_url(self) -> str:
        success_url = reverse_lazy(
            'posts:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
        return success_url


class CommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get_object(self):
        post = Post.objects.get(id=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.all()

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
        success_url = reverse_lazy(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        )
        return success_url


class FollowView(LoginRequiredMixin, RedirectView):
    template_name = 'posts/profile.html'

    def get(self, *args, **kwargs):
        if self.kwargs['username'] == self.request.user.username:
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.kwargs['username']}
                )
            )
        if Follow.objects.filter(
            author__username=self.kwargs['username'],
            user=self.request.user
        ).exists():
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.kwargs['username']}
                )
            )
        Follow.objects.create(
            author=User.objects.get(username=self.kwargs['username']),
            user=self.request.user
        )
        return super(FollowView, self).get(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy(
            'posts:profile_follow',
            kwargs={'username': self.kwargs['username']}
        )


class UnfollowView(LoginRequiredMixin, RedirectView):
    template_name = 'posts/profile.html'

    def get(self, *args, **kwargs):
        if Follow.objects.filter(
            author__username=self.kwargs['username'],
            user=self.request.user
        ).exists():
            Follow.objects.filter(
                author__username=self.kwargs['username'],
                user=self.request.user
            ).delete()
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.kwargs['username']}
                )
            )
        return super(UnfollowView, self).get(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy(
            'posts:profile_unfollow',
            kwargs={'username': self.kwargs['username']}
        )


class FollowIndexView(LoginRequiredMixin, ListView):
    model = Post
    title = 'Лента избранного'
    paginate_by = settings.PER_PAGE

    def get_posts(self):
        posts = Post.objects.filter(author__following__user=self.request.user)
        return posts

    def get_context_data(self, **kwargs):
        context = super(FollowIndexView, self).get_context_data(**kwargs)
        paginator = Paginator(self.get_posts(), self.paginate_by)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context['title'] = 'Последние обновления на сайте'
        context['page_obj'] = page_obj
        return context
