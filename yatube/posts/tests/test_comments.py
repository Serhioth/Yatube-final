from django.test import TestCase, Client
from posts.models import Post, Comment
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

User = get_user_model()


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(
            username='TestUser'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user
        )

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
        self.assertEqual(response.status_code, 200,
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
        self.assertEqual(response.status_code, 200,
                         'Страница не доступна')

        self.assertEqual(Comment.objects.all().count(),
                         comments_start_count + 1)

        self.assertRedirects(
            response,
            reverse_lazy(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
