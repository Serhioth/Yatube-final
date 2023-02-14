from django.test import TestCase, Client
from django.urls import reverse_lazy


class TestCustomErrors(TestCase):
    """
    Тест шаблонов кастомных ошибок
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client(enforce_csrf_checks=True)

    def test_custom_templates(self):
        response_404 = self.guest_client.get('/unexisted/')
        response_403 = self.guest_client.get(
            reverse_lazy(
                'posts:index'
            )
        )
        self.assertTemplateUsed(
            response_404,
            'core/404.html'
        )
        self.assertTemplateUsed(
            response_403,
            'core/403csrf.html'
        )
