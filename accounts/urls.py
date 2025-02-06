from __future__ import annotations

from django.urls import path

from .views import MeView, VerifyTokenView, DiscordSocialAuthView

urlpatterns = [
    path('discord/', DiscordSocialAuthView.as_view()),
    path('me/', MeView.as_view()),
    path('verify-token/', VerifyTokenView.as_view()),
]
