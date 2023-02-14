from django.test import TestCase, Client


class StaticPagesUrlTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_urls_is_existed_in_expected_locations(self):
        """Проверка доступности страниц по указанным адресам"""
        responses = [
            self.guest_client.get('/about/author/'),
            self.guest_client.get('/about/tech/')
        ]

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, 200,
                                 'Ошибка получения страницы по данному адресу')

    def test_about_pages_have_correct_templates(self):
        """Проверка, что по заданным адресам открываются корректные шаблоны"""
        responses = {
            self.guest_client.get('/about/author/'): 'about/author.html',
            self.guest_client.get('/about/tech/'): 'about/tech.html'
        }

        for response, template in responses.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template,
                                        'Запрос выдаёт неверный шаблон')
