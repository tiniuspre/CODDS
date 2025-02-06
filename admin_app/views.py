from __future__ import annotations

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from system.models import UserContainer
from codds.settings import MANAGER_HANDLER


def get_container_data(user_id: str, challenge_name: str) -> UserContainer:
    user = get_user_model().objects.get(id=user_id)
    container_data = get_object_or_404(UserContainer, user=user, challenge_name=challenge_name)
    return container_data


@permission_classes([IsAdminUser])
class ChallengesView(APIView):
    def get(self, request: Request) -> Response:
        return Response(data=MANAGER_HANDLER.get_challenge_names(), status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class ContainersView(APIView):
    def get(self, request: Request, challenge_name: str) -> Response:
        manager = MANAGER_HANDLER.get_manager(challenge_name)
        response = {}

        for challenge in UserContainer.objects.filter(challenge_name=challenge_name):
            container_data = get_container_data(challenge.user.id, challenge_name)
            response[challenge.user.id] = manager.get_container(container_data.identifier).__dict__()

        return Response(data=response, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class UsersAdminView(APIView):
    def get(self, request: Request) -> Response:
        users = get_user_model().objects.all()
        return Response(data=[user.__json__() for user in users], status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class UserAdminView(APIView):
    def get(self, request: Request, user_id: str) -> Response:
        user = get_user_model().objects.get(id=user_id)
        return Response(data=user.__json__(), status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class ContainersByUserView(APIView):
    def get(self, request: Request, user_id: str) -> Response:
        containers = UserContainer.objects.filter(user_id=user_id)
        res = []
        for container in containers:
            manager = MANAGER_HANDLER.get_manager(container.challenge_name)
            res.append(manager.get_container(container.identifier).__dict__())

        return Response(data=res, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class ContainerByUserView(APIView):
    def get(self, request: Request, challenge_name: str, user_id: str) -> Response:
        manager = MANAGER_HANDLER.get_manager(challenge_name)
        container_data = get_container_data(user_id, challenge_name)

        return Response(data=manager.get_container(container_data.identifier).__dict__(), status=status.HTTP_200_OK)

    def delete(self, request: Request, challenge_name: str, user_id: str) -> Response:
        manager = MANAGER_HANDLER.get_manager(challenge_name)
        container_data = get_container_data(user_id, challenge_name)

        manager.stop(container_data.identifier)

        return Response(status=status.HTTP_200_OK)
