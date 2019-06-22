from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.list import ListView

from .models import Post


class AllPostsView(ListView):
    ''' Выводит все посты в обратном хронологическом порядке.
    Нужно для страницы Home. ''' 
    model = Post
    template_name = 'pages/home.html'
    context_object_name = 'posts'


class FeedView(View):
    ''' Отвечает за вывод новостной ленты конкретного пользователя.
    Реализует пометку прочитанного. '''
    pass


class UserPostsView(View):
    ''' Выводит список постов одного пользователя. '''
    pass


class MyPostsView(View):
    ''' Выводит посты авторизованного пользователя. '''
    pass


class AddPostView(View):
    ''' Реализует добавление нового поста. '''
    pass


class DetailPostView(View):
    ''' Просмотр поста. Если пользователь авторизован и он является автором, 
    то он может редактировать/удалять пост.'''
    pass


class SubscriptionsView(View):
    ''' Просмотр списка пользователей и подписок. '''
    pass