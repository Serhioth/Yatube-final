from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from posts.models import Post, Group
from django.core.cache import cache


User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestingUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.responses = {
            'index':
                cls.authorized_client.get('/'),
            'groups':
                cls.authorized_client.get(f'/group/{cls.group.slug}/'),
            'profile':
                cls.authorized_client.get(f'/profile/{cls.user.username}/'),
            'post_detail':
                cls.authorized_client.get(f'/posts/{cls.post.id}/'),
            'post_create':
                cls.authorized_client.get('/create/'),
            'post_edit':
                cls.authorized_client.get(f'/posts/{cls.post.id}/edit/')
        }

    def setUp(self) -> None:
        super().setUp()
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
                'posts/create_post.html'
        }
        for response, template in responses.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template,
                                        'Использован неверный шаблон')

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
