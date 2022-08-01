from dependency_injector import containers, providers
from backend.src.dependencies.mongo_client import AppMongoClient
from backend.src.dependencies.scheduler import AppScheduler


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["backend.src.api.task"])
    mongo_client = providers.Singleton(AppMongoClient)
    scheduler = providers.Singleton(AppScheduler, mongo_client=mongo_client.provider)
