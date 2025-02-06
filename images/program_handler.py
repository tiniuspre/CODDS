import os
import json
from pathlib import Path
from typing import TypedDict, List, Dict

PROGRAM_HANDLER_BASE_DIR = Path(__file__).resolve().parent


class ExposedPort(TypedDict):
    port: int
    protocol: str


class ProcessData(TypedDict, total=False):
    dockerfile: str
    exposed_ports: List[ExposedPort]
    environment: Dict[str, str]
    network: str


Processes = Dict[str, ProcessData]


class Info(TypedDict):
    challenge_name: str
    challenge_description: str
    challenge_pin: str
    connection_type: str
    connection_port: int
    username: str
    password: str


class ChallengeData(TypedDict):
    info: Info
    processes: Processes


class Ports:
    def __init__(self, port: int, protocol: str):
        self.port = port
        self.protocol = protocol

    def __dict__(self):
        return {
            "port": self.port,
            "protocol": self.protocol
        }


class Process:
    def __init__(self, data: ProcessData, name, path: str):
        self.dockerfile = path + '/' + data["dockerfile"]
        self.exposed_ports = [
            Ports(x["port"], x["protocol"]) for x in data.get("exposed_ports", [])
        ]
        self.environment = data["environment"]
        self.network = data.get("network")
        self.name = name

    def update_network(self, network: str):
        self.network = network

    def has_ports(self):
        return len(self.exposed_ports) > 0

    def __dict__(self):
        return {
            "dockerfile": self.dockerfile,
            "exposed_ports": [{"port": port.port, "protocol": port.protocol} for port in self.exposed_ports],
            "environment": self.environment,
            "network": self.network
        }


class ChallengeInfo:
    def __init__(self, data: Info):
        self._data = data
        self.challenge_name = data["challenge_name"]
        self.challenge_description = data["challenge_description"]
        self.challenge_pin = data.get("challenge_pin")
        self.connection_type = data["connection_type"]
        self.connection_port = data["connection_port"]
        self.password = data.get("password")
        self.username = data.get("username")
        self.container_id = None

    def set_container_id(self, container_id: str):
        self.container_id = container_id

    def __dict__(self):
        return {
            "challenge_name": self.challenge_name,
            "challenge_description": self.challenge_description,
            "challenge_pin": self.challenge_pin,
            "connection_type": self.connection_type,
            "connection_port": self.connection_port,
            "container_id": self.container_id,
            "username": self.username,
            "password": self.password
        }


class Challenge:
    def __init__(self, data: ChallengeData, path: str):
        self.info = ChallengeInfo(data["info"])
        self.processes = [Process(proc_data, name, path) for name, proc_data in data["processes"].items()]

    def __dict__(self):
        return {
            "info": self.info.__dict__(),
            "processes": {process.name: process.__dict__() for process in self.processes}
        }


class ImageHandler:
    def __init__(self):
        self.images = {}
        self._discover_images()

    def _discover_images(self):
        for dir_name in os.listdir(PROGRAM_HANDLER_BASE_DIR):
            if os.path.isfile(PROGRAM_HANDLER_BASE_DIR / dir_name) or dir_name == '__pycache__':
                continue
            self.images[dir_name] = self.load_challenge(dir_name)
            self._create_network(dir_name)

    @staticmethod
    def _load_challenge_json(dir_name: str) -> ChallengeData:
        with open(os.path.join(PROGRAM_HANDLER_BASE_DIR / dir_name / 'config.json'), 'r') as file:
            return json.load(file)

    def load_challenge(self, dir_name: str) -> Challenge:
        return Challenge(self._load_challenge_json(dir_name), dir_name)

    def _create_network(self, challenge_name: str):
        for process in self.images[challenge_name].processes:
            process.update_network(challenge_name + "_network")


if __name__ == '__main__':
    image_handler = ImageHandler()
    print(image_handler.images.items())

