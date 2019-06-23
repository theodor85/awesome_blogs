from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    name = models.CharField(_("Name of User"), blank=True, max_length=255,
        unique=True)
    email = models.EmailField(verbose_name='Е-mail пользователя')

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
