from django.test import TestCase, Client
from posts.models import Post, Follow
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from http import HTTPStatus

User = get_user_model()


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

        cls.first_user_post = Post.objects.create(
            text='FirstUserText',
            author=cls.first_user
        )

        cls.second_user_post = Post.objects.create(
            text='SecondUserText',
            author=cls.second_user
        )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_first_user = Client()
        self.authorized_first_user.force_login(self.first_user)

        self.authorized_second_user = Client()
        self.authorized_second_user.force_login(self.second_user)

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

        self.assertNotEqual(
            start_count,
            after_follow_count
        )

        unfollow_response = self.authorized_first_user.get(
            reverse_lazy(
                'posts:profile_unfollow',
                kwargs={'username': self.second_user.username}
            )
        )

        after_unfollow_count = Follow.objects.all().count()

        self.assertEqual(
            unfollow_response.status_code,
            HTTPStatus.FOUND
        )

        self.assertNotEqual(
            after_follow_count,
            after_unfollow_count
        )

    def test_follow_index(self):
        """
        Проверка корректности работы FollowIndex
        """
        follow_response = self.authorized_first_user.get(
            reverse_lazy(
                'posts:profile_follow',
                kwargs={'username': self.second_user.username}
            )
        )
        responses = {
            'first_follow_index_response': self.authorized_first_user.get(
                reverse_lazy('posts:follow_index')
            ),
            'second_follow_index_response': self.authorized_second_user.get(
                reverse_lazy('posts:follow_index')
            )
        }

        self.assertEqual(
            follow_response.status_code,
            HTTPStatus.FOUND
        )

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
