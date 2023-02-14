from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TestUserForms(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Testing')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_creation_form(self):
        """Проверяем корректность работы формы регистрации"""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_creation(self):
        """Проверяем корректность работы формы регистрации"""
        # Ещё один юзер создаётся в setUpClass,
        # поэтому ожидаем в бд двух юзеров
        user_count_expected = 2
        form_data = {
            'first_name': 'Testname',
            'last_name': 'Testsurname',
            'username': 'Testusername',
            'email': 'test@test.com',
            'password1': 'a7s6d5f4g3',
            'password2': 'a7s6d5f4g3'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=form_data['username']))
        self.assertEqual(User.objects.count(), user_count_expected)
