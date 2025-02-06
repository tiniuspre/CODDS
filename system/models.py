from __future__ import annotations

from django.db import models


class UserContainer(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    challenge_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    identifier = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'challenge_name')

    def __str__(self):
        return self.challenge_name + ' - ' + self.user.username
