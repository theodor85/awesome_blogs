from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Subscriptions
from .forms import Subscriptions_formset
from awesome_blogs.users.models import User


class AllPostsView(ListView):
    ''' Выводит все посты в обратном хронологическом порядке.
    Нужно для страницы Home. ''' 
    model = Post
    template_name = 'pages/home.html'
    context_object_name = 'posts'


class FeedView(View):
    ''' Отвечает за вывод новостной ленты конкретного пользователя.
    Реализует пометку прочитанного. '''
    def get(self, request):
        return render(request, 'pages/subscriptions.html', {'a': 'DEBUG - FEED'})


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


class SubscriptionsView(LoginRequiredMixin, View):
    ''' Просмотр списка пользователей и подписок. '''

    #----- GET ---------

    def get(self, request):
        ''' Выводит с помощью набора форм список всех пользователей
        и ставит галочки у тех, на кого подписан текущий пользователь. '''
        
        self.get_all_users_except_self_and_admins()
        self.get_user_subscribe_to()
        self.set_initial_for_formset()
        context = self.get_context_with_formset()
        return render(request, 'pages/subscriptions.html', context)

    def get_all_users_except_self_and_admins(self):
        self.all_users = User.objects.exclude(name=self.request.user.name)
        self.all_users = self.all_users.exclude(is_staff=True)

    def get_user_subscribe_to(self):
        ''' На кого текущий юзер подписан? '''
        my_subscriptions = Subscriptions.objects.filter(user=self.request.user)
        self.users_subscriptions = [sub.subscribe_to for sub in my_subscriptions]

    def set_initial_for_formset(self):
        ''' Формируем список из всех имен пользователей,
        для тех, кто есть в подписках ставим True (в форме это будет галочка).
        '''
        self.initial = [ 
            {
                'username': user.name, 
                'subscribe': user in self.users_subscriptions
            } for user in self.all_users
        ]

    def get_context_with_formset(self):
        subscriptions_formset = Subscriptions_formset(initial=self.initial)
        context = {'formset': subscriptions_formset}
        return context

    #----- POST ---------

    def post(self, request):
        subscriptions_formset = Subscriptions_formset(request.POST)
        context = {'a': 'Привет'}
        return render(request, 'pages/subscriptions.html', context)
        # if subscriptions_formset.is_valid():
        #     subscriptions_formset.save()