from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):

    username = None

    phone_number = models.CharField(
        max_length=20,
        unique=True
    )

    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number