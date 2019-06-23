from django import forms
from django.forms import formset_factory


class SubscriptionForm(forms.Form):
    username = forms.CharField(label='Блог пользователя', disabled=True)
    subscribe = forms.BooleanField(label='Подписаться')


Subscriptions_formset = formset_factory(form=SubscriptionForm, extra=0)