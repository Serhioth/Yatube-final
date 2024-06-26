from django.contrib import admin

from posts.models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group',
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'title',
                    'description',
                    )

    search_fields = ('title', 'description')
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'author',
        'pub_date',
        'post'
    )
    list_editable = (
        'author',
        'text'
    )
    search_fields = (
        'author',
        'text'
    )
    list_filter = (
        'pub_date',
        'author'
    )
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'user'
    )
    list_editable = (
        'author',
        'user'
    )
    search_fields = (
        'author',
        'user'
    )
    list_filter = (
        'author',
        'user'
    )
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
