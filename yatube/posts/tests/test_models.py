from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from posts.models import Comment, Follow, Group, Post

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
            'group': 'Группа',
            'image': 'Картинка'
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
            'slug': 'Слаг группы',
            'description': 'Описание группы'
        }

        for field, expected in group_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_group._meta.get_field(field).verbose_name,
                    expected,
                    f'verbose_name {field} не соответствует ожидаемому'
                )

    def test_help_text(self):
        """Help_text в полях Group совпадает с ожидаемым"""
        task_group = self.group

        group_expected_names = {
            'title': 'Группа',
            'slug': 'Слаг группы',
            'description': 'Описание группы'
        }
        for field, expected in group_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_group._meta.get_field(field).help_text,
                    expected,
                    f'help_text {field} не соответствует ожидаемому'
                )


class TestCommentModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            username='CommentTestUser'
        )

        cls.post = Post.objects.create(
            text='TestCommentsText',
            author=cls.user
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='TestCommentsText'
        )

    def test_comment_verbose_name(self):
        """Verbose_name в полях Comment совпадает с ожидаемым"""
        task_comment = self.comment

        comment_expected_names = {
            'post': 'Связанный пост',
            'author': 'Автор коммента',
            'text': 'Текст комментария'
        }

        for field, expected in comment_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_comment._meta.get_field(field).verbose_name,
                    expected,
                    f'verbose_name {field} не соответствует ожидаемому'
                )

    def test_help_text(self):
        """Help_text в полях Comment совпадает с ожидаемым"""
        task_comment = self.comment

        comment_expected_names = {
            'post': 'Пост, к которому привязан комментарий',
            'author': 'Автор комментария',
            'text': 'Текст комментария'
        }
        for field, expected in comment_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_comment._meta.get_field(field).help_text,
                    expected,
                    f'help_text {field} не соответствует ожидаемому'
                )


class TestFollowModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            username='FollowUser'
        )
        cls.author = User.objects.create(
            username='FollowAuthor'
        )

        cls.following = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_follow_verbose_name(self):
        """Verbose_name в полях Follow совпадает с ожидаемым"""
        task_following = self.following

        following_expected_names = {
            'user': 'Подписчик',
            'author': 'Автор',
        }

        for field, expected in following_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_following._meta.get_field(field).verbose_name,
                    expected,
                    f'verbose_name {field} не соответствует ожидаемому'
                )

    def test_help_text(self):
        """Help_text в полях Follow совпадает с ожидаемым"""
        task_following = self.following

        following_expected_names = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected in following_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_following._meta.get_field(field).help_text,
                    expected,
                    f'help_text {field} не соответствует ожидаемому'
                )
