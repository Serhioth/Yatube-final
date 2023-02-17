import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post
from yatube.settings import PER_PAGE

User = get_user_model()


class TestPaginatorView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='TestingUser')
        cls.follow_user = User.objects.create(username='FollowTestUser')

        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.follow_user
        )

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.posts = []
        for num in range(13):
            time.sleep(0.1)
            cls.posts.append(
                Post.objects.create(
                    text='Text' + str(num),
                    author=cls.user,
                    group=cls.group
                )
            )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.follow_client = Client()
        self.follow_client.force_login(self.follow_user)

        self.responses = {
            'index':
                self.authorized_client.get(reverse('posts:index')),
            'groups':
                self.authorized_client.get(
                    reverse('posts:group_list',
                            kwargs={'slug': self.group.slug})),
            'profile':
                self.authorized_client.get(
                    reverse('posts:profile',
                            kwargs={'username': self.user.username})),
            'follow_index':
                self.follow_client.get(
                    reverse('posts:follow_index')
                )
        }

        self.responses_page_2 = {
            'index':
                self.authorized_client.get(reverse('posts:index') + '?page=2'),
            'groups':
                self.authorized_client.get(
                    reverse('posts:group_list',
                            kwargs={'slug': self.group.slug}) + '?page=2'),
            'profile':
                self.authorized_client.get(
                    reverse('posts:profile',
                            kwargs={'username': self.user.username})
                    + '?page=2'),
            'follow_index':
                self.follow_client.get(
                    reverse('posts:follow_index') + '?page=2'
                )
        }
        cache.clear()

    def test_show_10_posts_per_page(self):
        """Проверяем корректность работы паджинатора"""
        for response in self.responses.values():
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj']), PER_PAGE)

    def test_rest_of_posts(self):
        """Проверяем вторую страницу паджинатора"""
        for response in self.responses_page_2.values():
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']),
                    Post.objects.all().count()
                    - PER_PAGE
                )
