from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    email = models.EmailField(verbose_name='Е-mail пользователя')
    # подписки - это ссылки на других пользователей
    subscriptions = models.ForeignKey('self', on_delete=models.DO_NOTHING,
        null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
