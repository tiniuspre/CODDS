from __future__ import annotations

from datetime import timedelta

from rest_framework import status
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token

from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth import get_user_model

from codds.settings import FRONTEND_URL
from lib.social_account.discord import Discord

discord = Discord()


@permission_classes((AllowAny,))
class DiscordSocialAuthView(GenericAPIView):
    def get(self, request: Request) -> HttpResponseRedirect | Response:
        code = request.GET.get('code')

        if not code:
            return Response('no valid code', status=status.HTTP_400_BAD_REQUEST)

        discord_data = discord.exchange_code(code)
        discord_user_data = discord.get_user_data(discord_data['access_token'])
        discord_user_id = discord_user_data.get('id')
        if not get_user_model().objects.filter(id=discord_user_id).exists():
            user = get_user_model().objects.create(
                id=discord_user_id,
                username=discord_user_data.get('username'),
                email=discord_user_data.get('email'),
                avatar=discord_user_data.get('avatar'),
                access_token=discord_data.get('access_token'),
                refresh_token=discord_data.get('refresh_token'),
                token_expires_on=timezone.now() + timedelta(seconds=discord_data.get('expires_in')),
                token_type=discord_data.get('token_type'),
            )
            user.save()
        else:
            user = get_user_model().objects.get(id=discord_user_id)
            user.access_token = discord_data.get('access_token')
            user.refresh_token = discord_data.get('refresh_token')
            user.token_expires_on = timezone.now() + timedelta(seconds=discord_data.get('expires_in'))
            user.token_type = discord_data.get('token_type')
            user.save()
            Token.objects.filter(user=user).delete()

        Token.objects.create(user=user)
        new_token = list(Token.objects.filter(user_id=user).values('key'))

        return HttpResponseRedirect(FRONTEND_URL + f'/auth/discord?token={new_token[0]["key"]}')


class VerifyTokenView(GenericAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class MeView(GenericAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = request.user
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar,
                'is_staff': user.is_staff,
            }
        )
