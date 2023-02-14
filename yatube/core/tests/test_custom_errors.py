from django.test import TestCase, Client
from django.http import HttpResponseForbidden, Http404


class TestCustomErrors(TestCase):
    """
    Тест шаблонов кастомных ошибок
    """
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_custom_templates(self):
        self.assertTemplateUsed(
            self.guest_client.get(Http404),
            'core/404.html'
        )
        self.assertTemplateUsed(
            self.guest_client.get(HttpResponseForbidden),
            'core/403csrf.html'
        )
