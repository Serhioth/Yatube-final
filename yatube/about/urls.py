# about/urls.py
from django.urls import path

from about.views import AuthorPage, TechPage

app_name = 'about'

urlpatterns = [
    path('author/', AuthorPage.as_view(), name='author'),
    path('tech/', TechPage.as_view(), name='tech')
]
