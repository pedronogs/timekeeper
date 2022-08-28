from dependency_injector import containers, providers
from .mongo_client import AppMongoClient
from .scheduler import AppScheduler
from .docker_client import AppDockerClient


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["backend.src.api.task"])
    docker_client = providers.Singleton(AppDockerClient)
    mongo_client = providers.Singleton(AppMongoClient)
    scheduler = providers.Singleton(AppScheduler, mongo_client=mongo_client.provider)
