# Generated by Django 2.2.16 on 2023-02-08 17:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0011_auto_20230207_2041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст комментария', verbose_name='Текст комментария')),
                ('pub_date', models.DateTimeField(auto_now_add=True, help_text='Дата публикации', verbose_name='Дата публикации')),
                ('author', models.ForeignKey(help_text='Автор комментария', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор коммента')),
                ('post', models.ForeignKey(help_text='Пост, к которому привязан комментарий', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Связанный пост')),
            ],
            options={
                'verbose_name': 'Коммент',
                'verbose_name_plural': 'Комменты',
                'ordering': ('-pub_date',),
            },
        ),
    ]
