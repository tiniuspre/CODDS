from __future__ import annotations

import os

import docker
import docker.models.networks as docker_networks
from docker.models.containers import Container

from codds import settings
from images.program_handler import PROGRAM_HANDLER_BASE_DIR, Process, Challenge, ImageHandler
from system.dockermanager_exeptions import InvalidPinException

docker_client = docker.from_env()

DEFAULT_DOCKER_NETWORK = os.getenv('DEFAULT_DOCKER_NETWORK', 'manager_default')
BACKEND_DOMAIN = os.getenv('BACKEND_DOMAIN', 'localhost')


class DockerContainer:
    def __init__(self, identifier: str, process_data: Process, connection_type: str, network_id: str):
        self.identifier = identifier
        self.process_data = process_data
        self.docker_file = process_data.dockerfile
        self.container_id = identifier + '_' + process_data.name
        self.network = network_id
        self.ports = process_data.exposed_ports
        self.environment = process_data.environment
        self.container = None
        self.connection_type = connection_type

    def get_container(self) -> Container:
        if self.container is None:
            raise ValueError('Container not running')
        return self.container

    def _get_traefik_labels(self) -> dict:
        labels = {
            'traefik.enable': 'true',
            'traefik.docker.network': DEFAULT_DOCKER_NETWORK,
        }

        http_port = str(self.ports[0].port) if self.ports else '80'
        labels.update(
            {
                f'traefik.http.routers.{self.container_id}.rule': f'Host(`{self.identifier}.{BACKEND_DOMAIN}`)',
                f'traefik.http.routers.{self.container_id}.entrypoints': 'websecure',
                f'traefik.http.routers.{self.container_id}.tls': 'true',
                f'traefik.http.services.{self.container_id}.loadbalancer.server.port': http_port,
            }
        )

        return labels

    def run(self) -> Container:
        labels = {}
        if self.process_data.has_ports():
            labels.update(self._get_traefik_labels())

        container = docker_client.containers.run(
            image=self.docker_file.split('/')[0] + ':latest',
            name=self.container_id,
            environment=self.environment,
            network=DEFAULT_DOCKER_NETWORK,
            labels=labels,
            detach=True,
        )

        # Connect to Traefik network
        traefik_net = docker_client.networks.get(self.network)
        traefik_net.connect(container)
        self.container = container

        return container

    def stop(self) -> None:
        traefik_net = docker_client.networks.get(DEFAULT_DOCKER_NETWORK)

        traefik_net.disconnect(self.get_container())
        self.get_container().stop()
        self.get_container().remove()

    def is_online(self) -> bool:
        return self.container.status == 'created'

    def __dict__(self):
        return {
            'identifier': self.identifier,
            'container_id': self.container_id,
            'ports': [port.__dict__() for port in self.ports],
            'exists': True,
            'is_online': self.is_online(),
        }


class ContainerGroup:
    def __init__(self, identifier: str, challenge: Challenge, pin_code: str | None = None):
        self.identifier = identifier
        self.challenge = challenge
        self.network = self.create_network()
        self.pin = pin_code
        self.processes = {
            process.dockerfile: DockerContainer(identifier, process, challenge.info.connection_type, self.network.id) for process in challenge.processes
        }

    def create_network(self) -> docker_networks.Network:
        network = docker_client.networks.create(self.identifier + '_' + self.challenge.processes[0].network)
        return network

    def stop(self) -> None:
        for process in self.processes.values():
            process.stop()

    def start(self) -> None:
        if self.challenge.info.challenge_pin is not None and self.pin != self.challenge.info.challenge_pin:
            raise InvalidPinException('Invalid Pin')
        for process in self.processes.values():
            process.run()
            self.challenge.info.set_container_id(process.container_id)

    def __dict__(self):
        return {
            'exists': True,
            'identifier': self.identifier,
            'challenge_name': self.challenge.info.challenge_name,
            'processes': {process_name: process.__dict__() for process_name, process in self.processes.items()},
            'connection': {
                'type': self.challenge.info.connection_type,
                'port': self.challenge.info.connection_port,
                'url': f'{self.identifier}.{settings.BACKEND_IP_OR_DOMAIN}',
                'username': self.challenge.info.username,
                'password': self.challenge.info.password,
            },
            'requires_pin': self.challenge.info.challenge_pin is not None,
        }


class DockerManager:
    def __init__(self, challenge: Challenge):
        self.containers: dict[str, ContainerGroup] = {}
        self.challenge = challenge
        self.build_image()

    def spawn(self, identifier: str, pin_code: str | None = None) -> None:
        group = ContainerGroup(identifier, self.challenge, pin_code)
        group.start()
        self.containers[identifier] = group

    def stop(self, identifier: str) -> None:
        group = self.containers.get(identifier)
        if group:
            group.stop()
            del self.containers[identifier]

    def build_image(self) -> None:
        for process in self.challenge.processes:
            name = process.dockerfile.split('/')[0]
            path_name = name
            dockerfile = process.dockerfile.split('/')

            if len(dockerfile) > 2:
                path_name = '/'.join(dockerfile[:-1])

            dockerfile = dockerfile[-1]
            docker_client.images.build(path=str(PROGRAM_HANDLER_BASE_DIR / path_name), tag=f'{name}:latest', dockerfile=dockerfile)

    def get_container(self, identifier: str) -> ContainerGroup:
        return self.containers.get(identifier)

    def get_all_containers(self) -> dict[str, ContainerGroup]:
        return self.containers

    def get_all_containers_dict(self) -> dict[str, dict]:
        return {identifier: group.__dict__() for identifier, group in self.containers.items()}


class ManagerHandler:
    def __init__(self):
        self.managers = {}
        self._discover_managers()

    def _discover_managers(self) -> None:
        img_handler = ImageHandler()
        for challenge_name, challenge in img_handler.images.items():
            self.managers[challenge_name] = DockerManager(challenge)

    def get_manager(self, challenge_name: str) -> DockerManager:
        return self.managers.get(challenge_name)

    def get_challenge_names(self) -> list[str]:
        return list(self.managers.keys())


if __name__ == '__main__':
    s_id = 5
    managers = ManagerHandler()
    challs = managers.get_challenge_names()
    manager = managers.get_manager(challs[0])
    manager.spawn(f'test-{s_id}')
    print(manager.get_container(f'test-{s_id}').__dict__())  # noqa: T201
    manager.stop(f'test{s_id}')
    print(manager.get_container(f'test-{s_id}').__dict__())  # noqa: T201
