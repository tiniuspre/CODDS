from __future__ import annotations

import hashlib
import secrets

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from django.http import Http404
from django.shortcuts import get_object_or_404

from system.models import UserContainer
from codds.settings import MANAGER_HANDLER
from docker_manager import DockerManager
from system.dockermanager_exeptions import InvalidPinExceptionError


def md5(data: str) -> str:
    return hashlib.md5(data.encode()).hexdigest()  # noqa


def create_identifier(request: Request, challenge_name: str) -> str:
    unique_md5_element = md5(f'{challenge_name}{request.user.id}{secrets.randbelow(100000)}')
    short_unique_md5_element = unique_md5_element[: len(unique_md5_element) // 4]
    return str(
        request.user.id
        + '-'
        + short_unique_md5_element[len(short_unique_md5_element) // 2 :]
        + '-'
        + short_unique_md5_element[0 : len(short_unique_md5_element) // 2]
    )


def get_manager(challenge_name: str) -> DockerManager:
    manager = MANAGER_HANDLER.get_manager(challenge_name)
    if not manager:
        raise Exception('Manager not found')
    return manager


class ImagesView(APIView):
    def get(self, request: Request) -> Response:
        return Response(data=MANAGER_HANDLER.get_challenge_names(), status=status.HTTP_200_OK)


class ImageView(APIView):
    def get(self, request: Request, challenge_name: str) -> Response:
        """
        Gets the container for a user
        :param request:
        :param challenge_name:
        :return:
        """
        manager = MANAGER_HANDLER.get_manager(challenge_name)
        query = UserContainer.objects.filter(user=request.user, challenge_name=challenge_name)

        if not query.exists():
            return Response(
                status=status.HTTP_200_OK,
                data={
                    'exists': False,
                    'challenge_name': manager.challenge.info.challenge_name,
                    'requires_pin': manager.challenge.info.challenge_pin is not None,
                },
            )
        try:
            data = manager.get_container(query.first().identifier).__dict__()
        except AttributeError:
            UserContainer.objects.filter(user=request.user, challenge_name=challenge_name).delete()
            return Response(status=status.HTTP_200_OK, data={'exists': False, 'challenge_name': challenge_name})

        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request: Request, challenge_name: str) -> Response:
        """
        Creates and starts a container for a user

        :param request:
        :param challenge_name:
        :return:
        """
        manager = MANAGER_HANDLER.get_manager(challenge_name)

        if UserContainer.objects.filter(user=request.user, challenge_name=challenge_name).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Container already exists'})

        identifier = create_identifier(request, challenge_name)
        UserContainer.objects.create(
            identifier=identifier,
            user=request.user,
            challenge_name=challenge_name,
        ).save()
        try:
            manager.spawn(identifier, pin_code=request.data.get('pin'))
        except InvalidPinExceptionError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid pin code'})

        return Response(status=status.HTTP_201_CREATED, data=manager.get_container(identifier).__dict__())

    def delete(self, request: Request, challenge_name: str) -> Response:
        """
        Deletes a container for a user

        :param request:
        :param challenge_name:
        :return:
        """
        manager = get_manager(challenge_name)
        container = get_object_or_404(UserContainer, challenge_name=challenge_name, user=request.user)
        if container.user != request.user:
            raise Http404
        manager.stop(container.identifier)
        container.delete()
        return Response(status=status.HTTP_200_OK, data={'exists': False, 'challenge_name': challenge_name})
