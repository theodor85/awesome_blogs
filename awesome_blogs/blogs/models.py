from django.db import models


class Post(models.Model):
    ''' Модель сущности постов пользователей. '''

    content = models.TextField(verbose_name='Текст поста')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
        verbose_name='Опубликовано')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
        related_name='posts')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']