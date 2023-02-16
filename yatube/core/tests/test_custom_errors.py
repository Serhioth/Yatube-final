from django.test import Client, TestCase
from django.urls import reverse_lazy


class TestCustomErrors(TestCase):
    """
    Тест шаблонов кастомных ошибок
    """
    def setUp(self) -> None:
        self.guest_client = Client()
        self.csrf_client = Client(enforce_csrf_checks=True)

    def test_custom_templates(self):
        self.assertTemplateUsed(
            self.guest_client.get('/unexisted/'),
            'core/404.html'
        )
        self.assertTemplateUsed(
            self.csrf_client.post(
                reverse_lazy(
                    'posts:index'
                )
            ),
            'core/403csrf.html'
        )
