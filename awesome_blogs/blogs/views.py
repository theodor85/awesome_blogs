from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models.signals import post_save

from .models import Post, Subscriptions, Feed
from .forms import Subscriptions_formset, PostForm
from .signals import send_notifications_and_refresh_feed
from awesome_blogs.users.models import User


# подключаем обработчик к сигналу
post_save.connect(send_notifications_and_refresh_feed)

class PaginatorMixin:
    ''' Класс-примесь для реализации пагинатора в ListView '''
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        paginator = context['paginator']
        context['page_range']= range(1, paginator.num_pages+1)
        return context

class AllPostsView(PaginatorMixin, ListView):
    ''' Выводит все посты в обратном хронологическом порядке.
    Нужно для страницы Home. ''' 
    model = Post
    template_name = 'pages/home.html'
    context_object_name = 'posts'


class FeedView(LoginRequiredMixin, PaginatorMixin, ListView):
    ''' Отвечает за вывод новостной ленты конкретного пользователя.
    Реализует пометку прочитанного. '''
    
    template_name = 'pages/feed.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        feeds = self.request.user.news_feed.all()
        feeds = feeds.order_by('-post__created_at')
        return feeds


class UserPostList(PaginatorMixin, ListView):
    ''' Базовый класс для вывода списка постов одного пользователя
     '''
    model = Post
    template_name = 'pages/post_list.html'
    context_object_name = 'posts'


class UserPostsView(UserPostList):
    ''' Выводит список постов одного пользователя. '''

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['username']= self.kwargs['username']
        return context

    def get_queryset(self):
        return Post.objects.filter(author__name=self.kwargs['username'])


class MyPostsView(LoginRequiredMixin, UserPostList):
    ''' Выводит посты авторизованного пользователя. '''
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['username']= self.request.user.name
        return context

    def get_queryset(self):
        return self.request.user.posts.all()


class AddPostView(LoginRequiredMixin, View):
    ''' Реализует добавление нового поста. '''
    
    def get(self, request):
        form = PostForm()
        form.fields['title'].widget.attrs.update({'class': 'form-control'})
        form.fields['content'].widget.attrs.update({'class': 'form-control'})
        return render(request, 'pages/create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        form.fields['title'].widget.attrs.update({'class': 'form-control'})
        form.fields['content'].widget.attrs.update({'class': 'form-control'})
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.add_message(request, messages.SUCCESS, 
                'Пост успешно создан')
            return render(request, 'pages/create_post.html', {'form': form})

        messages.add_message(request, messages.WARNING, 
                'Пост не создан!')
        return render(request, 'pages/create_post.html', {'form': form})


class DetailPostView(DetailView):
    ''' Просмотр поста. Если пользователь авторизован и он является автором, 
    то он может редактировать/удалять пост.'''
    model = Post
    template_name = 'pages/post_detail.html'


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
        ''' Принимает набор форм. Сохраняет подписки пользователя.
        Формирует ленту пользователя на основании подписок. '''

        self.subscriptions_formset = Subscriptions_formset(request.POST)
        if self.subscriptions_formset.is_valid():
            try:
                self.apply_subscriptions_changes()
            except Exception as ex:
                messages.add_message(request, messages.ERROR, 
                '''Произошла ошибка во время сохранения подписок! 
                Подписки не сохранены! {}'''.format(ex))
            else:
                messages.add_message(request, messages.SUCCESS, 
                'Подписки сохранены')
        else:
            messages.add_message(request, messages.WARNING, 
                'Подписки не сохранены! Проверьте заполнение полей.')

        context = {'formset': self.subscriptions_formset}
        return render(request, 'pages/subscriptions.html', context)

    def apply_subscriptions_changes(self):
        ''' Это метод решает задачу добавления только тех подписок, 
        которые отсутствуют, и удаления тех, которые существуют. '''

        for form in self.subscriptions_formset:
            is_subscribe = form.cleaned_data['subscribe']
            user_subscribe_to = User.objects.get( 
                name=form.cleaned_data['username'] )
            if is_subscribe:
                if self.subscription_exists(user_subscribe_to):
                    continue
                else:
                    self.create_new_subscription(user_subscribe_to)
                    self.add_feed(user_subscribe_to)
            else:
                if self.subscription_exists(user_subscribe_to):
                    self.delete_subscription(user_subscribe_to)
                    self.delete_from_feed(user_subscribe_to)
                else:
                    continue

    def subscription_exists(self, user_subscribe_to):
        subs = Subscriptions.objects.filter(user=self.request.user)
        subs = subs.filter(subscribe_to=user_subscribe_to)
        return subs.exists()

    def create_new_subscription(self, user_subscribe_to):
        sub = Subscriptions()
        sub.user = self.request.user
        sub.subscribe_to = user_subscribe_to
        sub.save()

    def add_feed(self, user_subscribe_to):
        posts = user_subscribe_to.posts.all()
        new_feed = [ 
            Feed(
                user=self.request.user, 
                post=one_post, 
                read=False
                ) 
            for one_post in posts
        ]
        Feed.objects.bulk_create(new_feed)

    def delete_subscription(self, user_subscribe_to):
        sub = Subscriptions.objects.get(user=self.request.user, 
            subscribe_to=user_subscribe_to)
        sub.delete()
                    
    def delete_from_feed(self, user_subscribe_to):
        feed_to_del = self.request.user.news_feed.all()
        feed_to_del = feed_to_del.filter(post__author=user_subscribe_to)
        feed_to_del.delete()


class MarkReadView(LoginRequiredMixin, View):
    ''' Помечает элемент ленты прочитанным. '''

    def post(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        feed.read = True
        feed.save()
        return redirect('blogs:feed')


class UnMarkReadView(LoginRequiredMixin, View):
    ''' Помечает элемент ленты непрочитанным. '''

    def post(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        feed.read = False
        feed.save()
        return redirect('blogs:feed')