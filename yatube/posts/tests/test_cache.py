from django.test import TestCase, Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from posts.models import Post, Group

User = get_user_model()


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='CacheTestUser'
        )

        cls.group = Group.objects.create(
            title='TestCacheGroup',
            slug='testcacheslug',
            description='TestCacheDescription'
        )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        """
        Тест правильности работы кэша
        """
        post = Post.objects.create(
            text='TestCacheText',
            author=self.user,
            group=self.group
        )

        responses = [
            self.authorized_client.get(
                reverse_lazy('posts:index')
            ),
            self.authorized_client.get(
                reverse_lazy(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                )
            )
        ]
        Post.objects.filter(id=post.id).delete()
        responses_after_delete = [
            self.authorized_client.get(
                reverse_lazy('posts:index')
            ),
            self.authorized_client.get(
                reverse_lazy(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                )
            ),
            self.authorized_client.get(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            )
        ]
        for response, response_after_delete in zip(
            responses,
            responses_after_delete
        ):
            with self.subTest(response=response):
                self.assertEqual(
                    response.content,
                    response_after_delete.content,
                    'Страница кэшируется неверно'
                )
        cache.clear()
        responses_after_cache_clear = [
            self.authorized_client.get(
                reverse_lazy('posts:index')
            ),
            self.authorized_client.get(
                reverse_lazy(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                )
            ),
            self.authorized_client.get(
                reverse_lazy(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            )
        ]
        for response, cache_clear_response in zip(
            responses,
            responses_after_cache_clear
        ):
            with self.subTest(response=response):
                self.assertNotEqual(
                    response.content,
                    cache_clear_response.content,
                    'Кэш страницы не удаляется'
                )
