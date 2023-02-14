from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post
from django.core.cache import cache

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def test_post_models_have_correct_object_name(self):
        "Проверка title"
        self.assertEqual(PostModelTest.post.text[:15],
                         str(self.post),
                         'Поле title не соответствует ожидаемому')

    def test_post_verbose_name(self):
        """Verbose_name в полях Post совпадает с ожидаемым"""
        task_post = PostModelTest.post

        post_expected_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for field, expected in post_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_post._meta.get_field(field).verbose_name,
                    expected,
                    f'verbose_name {field} не соответствует ожидаемому'
                )

    def test_help_text(self):
        """Help_text в полях Post совпадает с ожидаемым"""
        task_post = PostModelTest.post

        post_expected_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected in post_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_post._meta.get_field(field).help_text,
                    expected,
                    f'help_text {field} не соответствует ожидаемому'
                )


class TestGroupModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )

    def test_group_models_have_correct_object_name(self):
        """Проверяем корректность title"""
        self.assertEqual(self.group.title,
                         str(self.group),
                         'Поле title не соответствует ожидаемому')

    def test_group_verbose_name(self):
        """Verbose_name в полях Group совпадает с ожидаемым"""
        task_group = self.group

        group_expected_names = {
            'title': 'Группа, к которой будет относиться пост',
            'description': 'Описание группы'
        }

        for field, expected in group_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_group._meta.get_field(field).verbose_name,
                    expected)

        for field, expected in group_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_group._meta.get_field(field).verbose_name,
                    expected,
                    f'verbose_name {field} не соответствует ожидаемому'
                )
