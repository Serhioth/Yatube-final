from django.test import TestCase, Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from posts.models import Post

User = get_user_model()


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='CacheTestUser'
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

        response = self.authorized_client.get(
            reverse_lazy('posts:index')
        )

        Post.objects.filter(id=post.id).delete()

        response_after_delete = self.authorized_client.get(
            reverse_lazy('posts:index')
        )

        self.assertEqual(
            response.content,
            response_after_delete.content,
            'Страница кэшируется неверно'
        )

        cache.clear()

        response_after_cache_clear = self.authorized_client.get(
            reverse_lazy('posts:index')
        )

        self.assertNotEqual(
            response.content,
            response_after_cache_clear.content,
            'Кэш страницы не удаляется'
        )
