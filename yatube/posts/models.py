from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel


class Group(models.Model):
    title = models.CharField('Группа, к которой будет относиться пост',
                             max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание группы')

    def __str__(self) -> str:
        return self.title

    def __len__(self):
        return len(self.posts.all())


User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Связанный пост',
        help_text='Пост, к которому привязан комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор коммента',
        help_text='Автор комментария'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Текст комментария'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Коммент'
        verbose_name_plural = 'Комменты'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Подписан',
        help_text='Подписан'
    )
