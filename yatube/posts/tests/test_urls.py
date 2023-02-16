from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestingUser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.responses = {
            'index':
                self.authorized_client.get('/'),
            'groups':
                self.authorized_client.get(f'/group/{self.group.slug}/'),
            'profile':
                self.authorized_client.get(f'/profile/{self.user.username}/'),
            'post_detail':
                self.authorized_client.get(f'/posts/{self.post.id}/'),
            'post_create':
                self.authorized_client.get('/create/'),
            'post_edit':
                self.authorized_client.get(f'/posts/{self.post.id}/edit/'),
            'follow_index':
                self.authorized_client.get('/follow/'),
            'add_comment':
                self.authorized_client.post(
                    f'/posts/{self.post.id}/comment/',
                    data={'text': 'TestComment'},
                    follow=True
                )
        }
        cache.clear()

    def test_availability_of_pages(self):
        """Страницы открываются по указанным адресам"""
        for response in self.responses.values():
            with self.subTest(response=response):
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "Страница не доступна"
                )

    def test_error_404(self):
        """Проверка на появление ошибки 404"""
        response = self.guest_client.get('/unexisted_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            '404 не появляется'
        )

    def test_post_pages_have_correct_template(self):
        """Проверка корректности шаблонов"""
        responses = {
            self.responses['index']:
                'posts/index.html',
            self.responses['groups']:
                'posts/group_list.html',
            self.responses['profile']:
                'posts/profile.html',
            self.responses['post_detail']:
                'posts/post_detail.html',
            self.responses['post_create']:
                'posts/create_post.html',
            self.responses['post_edit']:
                'posts/create_post.html',
            self.responses['follow_index']:
                'posts/follow.html',
            self.responses['add_comment']:
                'posts/post_detail.html'
        }
        for response, template in responses.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template,
                                        'Использован неверный шаблон')

    def test_redirect_pages(self):
        """
        Проверка корректности работы страниц переадресации
        """
        responses = [
            self.authorized_client.get(
                f'/profile/{self.user.username}/follow/'
            ),
            self.authorized_client.get(
                f'/profile/{self.user.username}/unfollow/'
            )
        ]

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_anonymous(self):
        """Переадресация анонимного пользователя"""
        links = [
            '/create/',
            f'/posts/{self.post.id}/edit/'
        ]
        for link in links:
            response = self.guest_client.get(link)
            self.assertRedirects(
                response,
                '/auth/login/?next=' + link,
                status_code=HTTPStatus.FOUND
            )
