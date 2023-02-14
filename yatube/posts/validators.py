from django.forms import forms


def validate_not_empty(value):

    if value == '' or value.isspace():
        raise forms.ValidationError(
            'Пожалуйста, заполните поле корректно',
            params={'value': value}
        )
