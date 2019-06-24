from django import forms
from django.forms import formset_factory

from .models import Post

class SubscriptionForm(forms.Form):
    username = forms.CharField(label='Блог пользователя')
    subscribe = forms.BooleanField(label='Подписаться', required=False)


Subscriptions_formset = formset_factory(form=SubscriptionForm, extra=0)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content')