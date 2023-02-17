from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel


class Group(models.Model):
    title = models.CharField(
        'Группа, к которой будет относиться пост',
        max_length=200,
        help_text='Группа'
    )
    slug = models.SlugField(
        'Слаг группы',
        unique=True,
        help_text='Слаг группы'
    )
    description = models.TextField(
        'Описание группы',
        help_text='Описание группы'
    )

    def __str__(self) -> str:
        return self.title

    def __len__(self):
        return Post.objects.filter(group__slug=self.slug).count()


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
        blank=True,
        help_text='Изображение'
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

    def __str__(self):
        return self.text[:15]


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
        verbose_name='Автор',
        help_text='Автор'
    )

    class Meta():
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
