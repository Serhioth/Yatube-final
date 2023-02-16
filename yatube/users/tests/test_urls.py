from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TestUsersUrls(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(
            username='Testing',
            password='Testing'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_page_is_reacheable(self):
        """Проверяем корректность имён и шаблонов"""
        responses = {
            self.guest_client.get(reverse('users:signup')):
                'users/signup.html',
            self.guest_client.get(reverse('users:login')):
                'users/login.html',
            self.guest_client.get(reverse('users:password_reset_form')):
                'users/password_reset_form.html',
            self.guest_client.get(reverse('users:password_reset_confirm',
                                          kwargs={'uidb64': 'test',
                                                  'token': 'test'})):
                'users/password_reset_confirm.html',
            self.guest_client.get(reverse('users:password_reset_done')):
                'users/password_reset_done.html',
            self.authorized_client.get(reverse('users:password_change')):
                'users/password_change_form.html',
            self.authorized_client.get(reverse('users:password_change_done')):
                'users/password_change_done.html',
            self.authorized_client.get(reverse('users:logout')):
                'users/logged_out.html'
        }
        for response, template in responses.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response,
                                        template, f'{response} не доступен')
