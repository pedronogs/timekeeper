from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED


class AppScheduler:

    def __init__(self, mongo_client, database: str = "timekeeper", collection: str = "jobs"):
        self.scheduler = AsyncIOScheduler(executors={"threadpool": ThreadPoolExecutor(max_workers=10)})

        self.scheduler.add_jobstore(MongoDBJobStore(client=mongo_client()(), database=database, collection=collection))
        self.scheduler.add_listener(lambda x: print(x.retval), mask=EVENT_JOB_EXECUTED)

    def __call__(self) -> AsyncIOScheduler:
        return self.scheduler

    def start_scheduler(self) -> None:
        self.scheduler.start()