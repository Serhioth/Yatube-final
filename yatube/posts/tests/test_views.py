import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse_lazy
from posts.models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='TestingUser')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        super().setUp()
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.responses = {
            'index':
                self.authorized_client.get(reverse_lazy('posts:index')),
            'groups':
                self.authorized_client.get(
                    reverse_lazy('posts:group_list',
                                 kwargs={'slug': self.group.slug})),
            'profile':
                self.authorized_client.get(
                    reverse_lazy('posts:profile',
                                 kwargs={'username': self.user.username})),
            'post_detail':
                self.authorized_client.get(
                    reverse_lazy('posts:post_detail',
                                 kwargs={'post_id': self.post.id})),
            'post_create':
                self.authorized_client.get(reverse_lazy('posts:post_create')),
            'post_edit':
                self.authorized_client.get(
                    reverse_lazy('posts:post_edit',
                                 kwargs={'post_id': self.post.id}))
        }

    def test_page_get_correct_titles(self):
        """Проверка, что значение titles верно передано"""
        titles = [
            'Последние обновления на сайте',
            f'Сообщения группы {self.group.title}',
            f'Профиль пользователя {self.user.get_full_name()}',
            str(self.post),
            'Создание новой записи',
            'Редактирование записи'
        ]
        for response, title in zip(self.responses.values(), titles):
            with self.subTest(response=response):
                self.assertEqual(response.context.get('title'), title)

    def check_post(self, post):
        """Тесты для проверки постов"""
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertTrue(post.image)

    def test_context(self):
        """
        Тестируем, что на страницы
        передаются правильные посты
        """
        posts = [
            self.responses['index'].context.get('page_obj')[0],
            self.responses['groups'].context.get('page_obj')[0],
            self.responses['profile'].context.get('page_obj')[0],
            self.responses['post_detail'].context['post'],
            self.responses['post_edit'].context['post']
        ]
        for post in posts:
            return self.check_post(post)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.first_user = User.objects.create(
            username='FirstFollowUser'
        )

        cls.second_user = User.objects.create(
            username='SecondFollowUser'
        )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_first_user = Client()
        self.authorized_first_user.force_login(self.first_user)

        self.authorized_second_user = Client()
        self.authorized_second_user.force_login(self.second_user)

        self.follow = Follow.objects.create(
            author=self.first_user,
            user=self.second_user
        )

    def test_follow(self):
        """
        Проверка корректности работы Follow
        """
        start_count = Follow.objects.all().count()
        follow_response = self.authorized_first_user.get(
            reverse_lazy(
                'posts:profile_follow',
                kwargs={'username': self.second_user.username}
            )
        )
        after_follow_count = Follow.objects.all().count()

        self.assertEqual(
            follow_response.status_code,
            HTTPStatus.FOUND
        )

        self.assertTrue(
            Follow.objects.filter(
                user=self.first_user,
                author=self.second_user
            ).exists()
        )

        self.assertNotEqual(
            start_count,
            after_follow_count
        )

    def test_unfollow(self):
        start_count = Follow.objects.all().count()

        unfollow_response = self.authorized_second_user.get(
            reverse_lazy(
                'posts:profile_unfollow',
                kwargs={'username': self.first_user.username}
            )
        )

        after_unfollow_count = Follow.objects.all().count()

        self.assertEqual(
            unfollow_response.status_code,
            HTTPStatus.FOUND
        )

        self.assertNotEqual(
            start_count,
            after_unfollow_count
        )

    def test_follow_index(self):
        """
        Проверка корректности работы FollowIndex
        """
        responses = {
            'first_follow_index_response': self.authorized_first_user.get(
                reverse_lazy('posts:follow_index')
            ),
            'second_follow_index_response': self.authorized_second_user.get(
                reverse_lazy('posts:follow_index')
            )
        }

        for response in responses.values():
            with self.subTest(response=response):
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

        self.assertNotEqual(
            responses['first_follow_index_response'].content,
            responses['second_follow_index_response'].content
        )
