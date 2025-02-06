from .views import DiscordSocialAuthView, MeView, VerifyTokenView

from django.urls import path

urlpatterns = [
    path('discord/', DiscordSocialAuthView.as_view()),
    path('me/', MeView.as_view()),
    path('verify-token/', VerifyTokenView.as_view()),
]