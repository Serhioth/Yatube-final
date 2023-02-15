import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestingUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

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
                            kwargs={'username': cls.user.username})),
            'post_detail':
                cls.authorized_client.get(
                    reverse('posts:post_detail',
                            kwargs={'post_id': cls.post.id})),
            'post_create':
                cls.authorized_client.get(reverse('posts:post_create')),
            'post_edit':
                cls.authorized_client.get(
                    reverse('posts:post_edit',
                            kwargs={'post_id': cls.post.id}))
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def test_page_uses_correct_template(self):
        """Проверка, что открываются верные шаблоны"""
        templates = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html'
        ]
        for response, template in zip(self.responses.values(), templates):
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template,
                                        f'Не тот шаблон {template}')

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
