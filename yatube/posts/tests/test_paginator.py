import time

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from yatube.settings import PER_PAGE
from django.core.cache import cache

User = get_user_model()


class TestPaginatorView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cache.clear()
        super().setUpClass()
        cls.user = User.objects.create(username='TestingUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

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

        cls.responses = {
            'index':
                cls.authorized_client.get(reverse('posts:index')),
            'groups':
                cls.authorized_client.get(
                    reverse('posts:group_list',
                            kwargs={'slug': cls.group.slug})),
            'profile':
                cls.authorized_client.get(
                    reverse('posts:profile',
                            kwargs={'username': cls.user.username}))
        }

        cls.responses_page_2 = {
            'index':
                cls.authorized_client.get(reverse('posts:index') + '?page=2'),
            'groups':
                cls.authorized_client.get(
                    reverse('posts:group_list',
                            kwargs={'slug': cls.group.slug}) + '?page=2'),
            'profile':
                cls.authorized_client.get(
                    reverse('posts:profile',
                            kwargs={'username': cls.user.username})
                    + '?page=2')
        }

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def test_show_10_posts_per_page(self):
        """Проверяем корректность работы паджинатора"""
        for response in self.responses.values():
            print(len(response.context['page_obj']))
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
