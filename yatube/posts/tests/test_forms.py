import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse_lazy

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            username='FormTestingUser'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        super().setUp()
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """
        Проверяем, создаётся ли через форму новый пост,
        проверяем корректность редиректа
        """
        post_count_start = Post.objects.all().count()

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
        form_data = {
            'text': 'TestText',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse_lazy('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse_lazy(
                'posts:profile',
                kwargs={
                    'username': self.user.username
                }
            )
        )
        self.assertEqual(
            Post.objects.count(),
            post_count_start + 1
        )
        self.assertTrue(
            Post.objects.filter
            (
                author=self.user,
                text=form_data['text'],
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_coments_form(self):
        """Проверка корректности работы формы Comment"""
        form = CommentForm()
        self.assertIn('text', form.fields)

    def test_posts_forms(self):
        """Проверка корректности работы формы Post"""
        form = PostForm()
        self.assertIn('text', form.fields)
        self.assertIn('group', form.fields)
        self.assertIn('image', form.fields)

    def post_is_edited(self):
        """
        Проверяем, что пост изменился,
        после отправки формы
        """
        post = Post.objects.create(
            text='EditText',
            author=self.user,
            group=self.group
        )
        another_group = Group.objects.create(
            title='This is different',
            slug='different',
            description='Totally another group'
        )
        form_data = {
            'text': 'I see you',
            'group': another_group.id
        }
        start_count = Post.objects.all().count()
        response = self.authorized_client.post(
            reverse_lazy(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse_lazy(
                'posts:posts_detail',
                kwargs={'post_id': post.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user
            ).exists()
        )
        self.assertEqual(
            Post.objects.all().count(),
            start_count
        )


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            username='TestUser'
        )

        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user
        )

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_anonymous_cant_comment(self):
        """Проверяем, что аноним не может комментировать"""
        comments_count = Comment.objects.all().count()

        form_data = {'text': 'You shall not pass!'}

        response = self.guest_client.post(
            reverse_lazy('posts:add_comment',
                         kwargs={'post_id': self.post.id}
                         ),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница не доступна')
        self.assertEqual(comments_count, 0,
                         'Анониму удалось отправить коммент')

    def test_authorized_can_comment(self):
        """
        Проверяем, что авторизованный пользователь
        может оставлять комментарии
        """
        comments_start_count = Comment.objects.all().count()

        form_data = {'text': 'Gotcha!'}

        response = self.authorized_client.post(
            reverse_lazy('posts:add_comment',
                         kwargs={'post_id': self.post.id}
                         ),
            data=form_data,
            follow=True
        )

        comments_after_post_count = Comment.objects.all().count()

        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                post=self.post,
                text=form_data['text']
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница не доступна')

        self.assertNotEqual(comments_start_count,
                            comments_after_post_count)

        self.assertRedirects(
            response,
            reverse_lazy(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
