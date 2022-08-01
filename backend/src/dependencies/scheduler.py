from pymongo import MongoClient

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class AppScheduler:

    def __init__(self, mongo_client, database: str = "timekeeper", collection: str = "jobs"):
        self.scheduler = AsyncIOScheduler()

        self.scheduler.add_jobstore(MongoDBJobStore(client=mongo_client()(), database="timekeeper", collection="jobs"))

    def __call__(self) -> AsyncIOScheduler:
        return self.scheduler

    def start_scheduler(self) -> None:
        self.scheduler.start()