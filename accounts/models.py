from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.CharField(max_length=50, blank=True, unique=True, primary_key=True)
    email = models.EmailField(unique=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=50, blank=True, unique=True)
    avatar = models.CharField(max_length=255, blank=True)
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    token_expires_on = models.DateTimeField(null=True, blank=True)
    token_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.email

    def is_token_expired(self):
        return timezone.now() > self.token_expires_on

    def __json__(self):
        return {
            'id': self.id,
            'email': self.email,
            'date_joined': self.date_joined,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'username': self.username,
            'avatar': self.avatar,
        }
