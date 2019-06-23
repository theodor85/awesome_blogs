from django.db import models


class Post(models.Model):
    ''' Модель сущности постов пользователей. '''

    content = models.TextField(verbose_name='Текст поста')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
        verbose_name='Опубликовано')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
        related_name='posts')

    def __str__(self):
        return '%s - %s' % (self.author.name, self.title)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']


class Feed(models.Model):
    ''' Модель сущности персональной ленты пользователя.
    Она нужна, в том числе для того, чтобы хранить флаг 
    'read' - прочитано/нерпочитано. 
    Каждая запись ссылается на один пост.'''

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
        related_name='news_feed')
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    read = models.BooleanField()


class Subscriptions(models.Model):
    ''' Модель подписок пользователя. '''

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
        related_name='my_subscriptions')
    subscribe_to = models.OneToOneField('users.User', 
        on_delete=models.CASCADE)