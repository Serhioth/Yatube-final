from django.test import TestCase
from django.http import HttpResponseForbidden, Http404


class TestCustomErrors(TestCase):
    """
    Тест шаблонов кастомных ошибок
    """
    def test_custom_templates(self):
        self.assertTemplateUsed(
            Http404,
            'core/404.html'
        )
        self.assertTemplateUsed(
            HttpResponseForbidden,
            'core/403csrf.html'
        )
